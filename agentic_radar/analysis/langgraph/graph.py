import ast
import os
from typing import Any, Dict, List, Optional, Union
import json


class GraphInstanceTracker(ast.NodeVisitor):
    """
    A node visitor that:
      1. Finds instantiations of the Graph class (by fully-qualified name).
      2. Tracks method calls on those instances, capturing arguments.
      3. Adds extra logic for 'add_conditional_edges' method:
         - If called with 2 args, the second is the name of a function -> gather return values
         - If called with 3 args, the third is a literal list/dict or a variable referencing one -> gather values
      4. Adds extra logic for "add_node" method:
         - If called with 1 positional argument -> gather information about it
         - If called with 2 positional arguments -> gather information about it
    """

    def __init__(
        self,
        graph_class_fqcn: str,
        command_class_fqn: str,
        add_conditional_edges_method_name: str,
        add_node_method_name: str,
        global_functions,
        global_variables,
    ):
        """
        graph_class_fqcn: The fully qualified class name of the Graph class to look for.
        command_class_fqcn: The fully qualified class name of the Command class to look for.
        add_conditional_edges_method_name: The method name that, when called, triggers addition of conditional edges.
        add_node_method_name: The method name that, when called, triggers addition of a node.
        """
        self.graph_class_fqcn = graph_class_fqcn
        self.command_class_fqn = command_class_fqn
        self.add_conditional_edges_method_name = add_conditional_edges_method_name
        self.add_node_method_name = add_node_method_name

        # Maintain a mapping of local import aliases to fully qualified paths.
        self.import_aliases: Dict[str, str] = {}

        # For "from examples.graph import Graph", store fully qualified references:
        self.import_aliases_fully: Dict[str, str] = {}

        self.instance_methods: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

        # Track which variables are instances of our target class.
        # If we see "g = Graph()", then self.variable_is_target_instance["g"] = True
        self.variable_is_target_instance: Dict[str, bool] = {}

        # Keep track of all top-level functions
        self.function_defs: Dict[str, Union[ast.FunctionDef, ast.AsyncFunctionDef]] = {}

        # Track variables that hold a literal list or dict, so that if a method is called
        # with that variable, we can retrieve its contents
        self.variable_values: Dict[str, Union[ast.List, ast.Dict]] = {}

        # Tracking global functions and variables that have lists or dictionaries as values for resolving imports
        self.global_functions = global_functions
        self.global_variables = global_variables

    def visit_Import(self, node: ast.Import) -> Any:
        """
        Handle statements like:
          import examples
          import examples.graph as ex
        """
        for alias in node.names:
            local_name = alias.asname if alias.asname else alias.name
            self.import_aliases[local_name] = alias.name

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        """
        Handle statements like:
          from examples.graph import Graph
          from examples import graph as gph
        """

        if node.module is None:
            self.generic_visit(node)
            return

        base_module = node.module
        for alias in node.names:
            local_name = alias.asname if alias.asname else alias.name
            self.import_aliases_fully[local_name] = f"{base_module}.{alias.name}"

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        """
        Record the top-level function definitions for later retrieval.
        """
        self.function_defs[node.name] = node
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        """
        Same as visit_FunctionDef, but for async functions.
        """
        self.function_defs[node.name] = node
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> Any:
        """
        Handle assignments, e.g.:
            g = Graph(...)
            my_list = [1, 2, 3]
            my_dict = {"foo": 42}
        We identify if the assigned value is a call to our target class
        or a list/dict.
        """
        # If there's exactly one target, and it's a Name, e.g., "x = ..."
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id

            # If the right side is a Call node, check if it instantiates the Graph class
            if isinstance(node.value, ast.Call):
                if self._call_is_target_class(node.value):
                    self.variable_is_target_instance[var_name] = True

            # If the right side is a list or dict, store it for later.
            if isinstance(node.value, (ast.List, ast.Dict)):
                self.variable_values[var_name] = node.value
            else:
                # If we reassign the variable to something else, remove from variable_values
                if var_name in self.variable_values:
                    del self.variable_values[var_name]

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> Any:
        """
        Resolving method calls on the target Graph class in order to get the arguments with which the methods were called.
        The "add_conditional_edges" and "add_node" methods are examined in more detail.
        """
        # The 'func' of a Call might be an Attribute like g.add_node
        if isinstance(node.func, ast.Attribute):
            # node.func.value might be a Name, e.g., 'g'
            if isinstance(node.func.value, ast.Name):
                instance_name = node.func.value.id

                # Check if that variable is an instance of our target class
                if self.variable_is_target_instance.get(instance_name, False):
                    method_name = node.func.attr

                    # A record of all the arguments of the call
                    call_record = {
                        "positional": [self._stringify_ast_node(a) for a in node.args],
                        "keyword": {
                            kw.arg: self._stringify_ast_node(kw.value)
                            for kw in node.keywords
                            if kw.arg is not None
                        },
                    }

                    if method_name == self.add_conditional_edges_method_name:
                        self._process_add_conditional_edges_method_call(
                            node, call_record
                        )

                    if method_name == self.add_node_method_name:
                        self._handle_add_node_argument(node, call_record)

                    if instance_name not in self.instance_methods:
                        self.instance_methods[instance_name] = {}
                    if method_name not in self.instance_methods[instance_name]:
                        self.instance_methods[instance_name][method_name] = []

                    self.instance_methods[instance_name][method_name].append(
                        call_record
                    )

        self.generic_visit(node)

    # Helpers

    def _handle_add_node_argument(self, call_node: ast.Call, call_record: dict) -> None:
        """
        Resolving the arguments of the "add_node" method in order to find all nodes, along with potential implicitly defined edges.
        """

        num_pos = len(call_node.args)
        if num_pos == 1:
            info, gotos = self._analyze_argument(call_node.args[0])
            call_record["node_definition_argument_info"] = info
            call_record["gotos"] = gotos

        elif num_pos == 2:
            info, gotos = self._analyze_argument(call_node.args[1])
            call_record["node_definition_argument_info"] = info
            call_record["gotos"] = gotos

    def _analyze_argument(self, node: ast.AST) -> Dict[str, Optional[str]]:
        """
        Return a dictionary describing the argument:
        - "original": how it appears in the code
        - "fq_name": best guess fully qualified name (if we can resolve)
        and all the possible values of the "goto" argument in the node definition if they exist. This is used to determine the implicitly defined edges.
        """
        result: Dict[str, Optional[str]] = {
            "original": self._stringify_ast_node(node),
            "fq_name": None,
        }

        gotos = []

        # 1) If it's a bare name (like "some_func")
        if isinstance(node, ast.Name):
            fq_name = self._resolve_fq_name(node)
            result["fq_name"] = fq_name

            if fq_name in self.function_defs:
                gotos = self._get_goto_arguments_of_returned_command_objects(
                    self.function_defs[fq_name]
                )

            elif fq_name in self.global_functions:
                gotos = self._get_goto_arguments_of_returned_command_objects(
                    self.global_functions[fq_name]
                )

        # 2) If it's an attribute, e.g. "some_import.func"
        elif isinstance(node, ast.Attribute):
            fq_name = self._resolve_fq_name(node)
            result["fq_name"] = fq_name

            if fq_name in self.function_defs:
                gotos = self._get_goto_arguments_of_returned_command_objects(
                    self.function_defs[fq_name]
                )

            elif fq_name in self.global_functions:
                gotos = self._get_goto_arguments_of_returned_command_objects(
                    self.global_functions[fq_name]
                )

        # 3) If it's a call, e.g. "some_import.function(...)" or "local_func(...)" or "Name()"
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, (ast.Name, ast.Attribute)):
                fq_name = self._resolve_fq_name(func)
                result["fq_name"] = fq_name

            else:
                result["fq_name"] = result["original"]

        return result, gotos

    def _process_add_conditional_edges_method_call(
        self, call_node: ast.Call, call_record: dict
    ) -> None:
        """
        Resolving the arguments of the "add_conditional_edges" method in order to find edges.
        """

        # Combine all arguments (positional + keyword) in source order.
        # The 'value' of each keyword is the actual expression.
        all_args_in_order = self._get_all_args_in_call(call_node)

        if len(all_args_in_order) == 2:
            second_arg = all_args_in_order[1]
            if isinstance(second_arg, ast.Name):
                func_name = second_arg.id
                if func_name in self.function_defs:
                    returns = self._get_return_expressions(
                        self.function_defs[func_name]
                    )
                    call_record["path"] = {"function_returns": returns}
                elif self._resolve_fq_name(second_arg) in self.global_functions:
                    returns = self._get_return_expressions(
                        self.global_functions[self._resolve_fq_name(second_arg)]
                    )
                    call_record["path"] = {"function_returns": returns}

        elif len(all_args_in_order) == 3:
            third_arg = all_args_in_order[2]

            if isinstance(third_arg, ast.List):
                list_vals = [self._stringify_ast_node(elt) for elt in third_arg.elts]
                call_record["path_map"] = {"list_values": list_vals}

            elif isinstance(third_arg, ast.Dict):
                dict_vals = [self._stringify_ast_node(v) for v in third_arg.values]
                call_record["path_map"] = {"dict_values": dict_vals}

            elif isinstance(third_arg, ast.Name):
                var_name = third_arg.id
                if var_name in self.variable_values:
                    val_node = self.variable_values[var_name]
                    if isinstance(val_node, ast.List):
                        list_vals = [
                            self._stringify_ast_node(elt) for elt in val_node.elts
                        ]
                        call_record["path_map"] = {"list_values": list_vals}
                    elif isinstance(val_node, ast.Dict):
                        dict_vals = [
                            self._stringify_ast_node(v) for v in val_node.values
                        ]
                        call_record["path_map"] = {"dict_values": dict_vals}
                elif self._resolve_fq_name(third_arg) in self.global_variables:
                    val_node = self.global_variables[self._resolve_fq_name(third_arg)]
                    if isinstance(val_node, ast.List):
                        list_vals = [
                            self._stringify_ast_node(elt) for elt in val_node.elts
                        ]
                        call_record["path_map"] = {"list_values": list_vals}
                    elif isinstance(val_node, ast.Dict):
                        dict_vals = [
                            self._stringify_ast_node(v) for v in val_node.values
                        ]
                        call_record["path_map"] = {"dict_values": dict_vals}

    def _call_is_target_class(self, call_node: ast.Call) -> bool:
        """
        Checks if the call instantiates our target Graph class
        """
        fq_name = self._resolve_fq_name(call_node.func)
        return fq_name == self.graph_class_fqcn

    def _resolve_fq_name(self, node: Union[ast.Name, ast.Attribute]) -> str:
        """
        Attempt to resolve a node to a fully qualified name
        """
        if isinstance(node, ast.Name):
            if node.id in self.import_aliases_fully:
                return self.import_aliases_fully[node.id]
            return self.import_aliases.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            base_fq = self._resolve_fq_name(node.value)
            if base_fq:
                return base_fq + "." + node.attr
            return node.attr
        return ""

    def _stringify_ast_node(self, node: ast.AST) -> str:
        """
        Convert an AST node into a string
        """
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return node.value
            return repr(node.value)
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Call):
            return f"Call({ast.dump(node)})"
        if isinstance(node, ast.List):
            return (
                "ListLiteral(["
                + ", ".join(self._stringify_ast_node(elt) for elt in node.elts)
                + "])"
            )
        if isinstance(node, ast.Dict):
            keys = [self._stringify_ast_node(k) for k in node.keys]
            vals = [self._stringify_ast_node(v) for v in node.values]
            pairs_str = ", ".join(f"{k}: {v}" for k, v in zip(keys, vals))
            return f"DictLiteral({{{pairs_str}}})"

        return ast.dump(node)

    def _get_all_args_in_call(self, call_node: ast.Call) -> List[ast.expr]:
        """
        Returns a list of all arguments (positional first, then each
        keyword argument's value) in the order they appear in the source.
        """
        combined = []
        combined.extend(call_node.args)

        for kw in call_node.keywords:
            combined.append(kw.value)
        return combined

    def _get_return_expressions(
        self, func_def: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> List[str]:
        """
        Traverse the body of a function definition and collect all returns
        """

        returns = []

        class ReturnCollector(ast.NodeVisitor):
            """
            Inner visitor class that visits Return nodes in the function body.
            We store them in the outer 'returns' list.
            """

            def __init__(inner_self, outer_self):
                super().__init__()
                inner_self.outer = outer_self
                inner_self.variables: Dict[str, str] = {}

            def visit_Return(inner_self, return_node: ast.Return):
                if return_node.value is not None and isinstance(
                    return_node.value, ast.Name
                ):
                    if return_node.value.id in inner_self.variables:
                        returns.extend(inner_self.variables[return_node.value.id])
                    else:
                        returns.append(
                            inner_self.outer._stringify_ast_node(return_node.value)
                        )
                if return_node.value is not None and isinstance(
                    return_node.value, ast.Constant
                ):
                    returns.append(return_node.value.value)

            def visit_Assign(inner_self, node: ast.Assign) -> Any:
                """
                Handle assignments in case code is like:
                if ...:
                    next_node = "node1"
                else:
                    next_node = "node2"

                return next_node
                """
                # If there's exactly one target, and it's a Name, e.g., "x = ..."
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    var_name = node.targets[0].id

                    # If the right side is a literal list or dict, store it for later.
                    if isinstance(node.value, ast.Constant):
                        # and node.value accounts for None
                        if (
                            var_name not in inner_self.variables
                            and node.value.value is not None
                        ):
                            inner_self.variables[var_name] = [node.value.value]
                        elif node.value.value:
                            inner_self.variables[var_name].append(node.value.value)
                    elif isinstance(node.value, ast.Name):
                        # example var1 = var2
                        if node.value.id in inner_self.variables:
                            inner_self.variables[var_name] = inner_self.variables[
                                node.value.id
                            ]
                        else:
                            inner_self.variables[var_name] = [
                                inner_self.outer._stringify_ast_node(node.value)
                            ]

        ReturnCollector(self).visit(func_def)
        return returns

    def _get_goto_arguments_of_returned_command_objects(
        self, func_def: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> List[str]:
        """
        Traverse the body of a function definition and collect all possible values of the "goto" argument of a returned Command object
        """

        gotos = set()

        class GotoCollector(ast.NodeVisitor):
            """
            Inner visitor class that visits Return nodes in the function body and sees if a Command object is returned.
            We store the values of the "goto" argument in the outer 'gotos' set.
            """

            def __init__(inner_self, outer_self):
                super().__init__()
                inner_self.outer = outer_self
                inner_self.variables: Dict[str, str] = {}

            def visit_Return(inner_self, return_node: ast.Return):
                if return_node.value is not None and isinstance(
                    return_node.value, ast.Call
                ):
                    call_node = return_node.value
                    # Ends with because we may be using global function definition in which we don't have access to fqn
                    if isinstance(
                        call_node.func, ast.Name
                    ) and inner_self.outer.command_class_fqn.endswith(
                        call_node.func.id
                    ):
                        for kw in call_node.keywords:
                            if kw.arg == "goto":
                                val_node = kw.value
                                if isinstance(val_node, ast.Constant) and isinstance(
                                    val_node.value, str
                                ):
                                    gotos.add(val_node.value)

                                elif isinstance(val_node, ast.List):
                                    for elt in val_node.elts:
                                        if isinstance(elt, ast.Constant) and isinstance(
                                            elt.value, str
                                        ):
                                            gotos.add(elt.value)

                                elif isinstance(val_node, ast.Name):
                                    var_name = val_node.id
                                    if var_name in inner_self.outer.variable_values:
                                        var_node = inner_self.outer.variable_values[
                                            var_name
                                        ]
                                        if isinstance(var_node, ast.List):
                                            list_vals = [
                                                self._stringify_ast_node(elt)
                                                for elt in var_node.elts
                                            ]
                                            for val in list_vals:
                                                gotos.add(val)
                                    elif var_name in inner_self.variables:
                                        list_vals = inner_self.variables[var_name]
                                        for val in list_vals:
                                            gotos.add(val)
                                    else:
                                        gotos.add(
                                            inner_self.outer._stringify_ast_node(
                                                val_node
                                            )
                                        )

            def visit_Assign(inner_self, node: ast.Assign) -> Any:
                """
                Handle assignments in case code is like:
                if ...:
                    next_node = "node1"
                else:
                    next_node = "node2"

                return Command(...goto=next_node)
                """
                # If there's exactly one target, and it's a Name, e.g., "x = ..."
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    var_name = node.targets[0].id

                    # If the right side is a literal list or dict, store it for later.
                    if isinstance(node.value, ast.Constant):
                        # and node.value accounts for None
                        if (
                            var_name not in inner_self.variables
                            and node.value.value is not None
                        ):
                            inner_self.variables[var_name] = [node.value.value]
                        elif node.value.value:
                            inner_self.variables[var_name].append(node.value.value)
                    elif isinstance(node.value, ast.Name):
                        # example var1 = var2
                        if node.value.id in inner_self.variables:
                            inner_self.variables[var_name] = inner_self.variables[
                                node.value.id
                            ]
                        else:
                            inner_self.variables[var_name] = [
                                inner_self.outer._stringify_ast_node(node.value)
                            ]
                    elif isinstance(node.value, ast.List):
                        if var_name not in inner_self.variables and node.value:
                            inner_self.variables[var_name] = [
                                self._stringify_ast_node(elt) for elt in node.value.elts
                            ]
                        elif node.value:
                            inner_self.variables[var_name].extend(
                                [
                                    self._stringify_ast_node(elt)
                                    for elt in node.value.elts
                                ]
                            )

        GotoCollector(self).visit(func_def)
        return gotos


def parse_python_file(
    filepath: str,
    target_class: str,
    command_class_fqn: str,
    add_conditional_edges_method_name: str,
    add_node_method_name: str,
    global_functions,
    global_variables,
) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Parse a single Python file for:
      - Instantiations of the Graph class
      - Method calls on those instances
    """

    source = ""
    if filepath.endswith(".py"):
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    elif filepath.endswith(".ipynb"):
        with open(filepath, "r", encoding="utf-8") as f:
            notebook = json.load(f)
            for cell in notebook["cells"]:
                if cell["cell_type"] == "code":
                    for row in cell["source"]:
                        source += row

    tree = ast.parse(source, filename=filepath)

    tracker = GraphInstanceTracker(
        target_class,
        command_class_fqn,
        add_conditional_edges_method_name,
        add_node_method_name,
        global_functions,
        global_variables,
    )

    tracker.visit(tree)

    return tracker.instance_methods


def walk_directory_and_parse(
    root_dir: str,
    target_class: str,
    command_class_fqn: str,
    add_conditional_edges_method_name: str,
    add_node_method_name: str,
    global_functions,
    global_variables,
) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Recursively walk a directory (root_dir), parse each .py file,
    and merge results for the target Graph class
    """
    combined_results: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py") or filename.endswith(".ipynb"):
                fullpath = os.path.join(dirpath, filename)
                file_results = parse_python_file(
                    fullpath,
                    target_class,
                    command_class_fqn,
                    add_conditional_edges_method_name,
                    add_node_method_name,
                    global_functions,
                    global_variables,
                )

                for instance_name, methods_dict in file_results.items():
                    if instance_name not in combined_results:
                        combined_results[instance_name] = {}
                    for method_name, calls in methods_dict.items():
                        if method_name not in combined_results[instance_name]:
                            combined_results[instance_name][method_name] = []
                        combined_results[instance_name][method_name].extend(calls)
                        combined_results[instance_name]["filepath"] = fullpath

    return combined_results


def parse_all_graph_instances_in_directory(
    root_directory,
    graph_class_fqcn,
    command_class_fqn,
    add_conditional_edges_method_name,
    add_node_method_name,
    global_functions,
    global_variables,
):

    results = walk_directory_and_parse(
        root_directory,
        graph_class_fqcn,
        command_class_fqn,
        add_conditional_edges_method_name,
        add_node_method_name,
        global_functions,
        global_variables,
    )
    graphs = []
    for graph, call_records in results.items():
        nodes = []
        basic_edges = []
        conditional_edges = []

        if call_records.get("add_node", False):
            call_data = call_records.get("add_node")
            for single_call in call_data:
                # The actual name if the method received 2 arguments, and the name of the function if it received one
                node_name = single_call["positional"][0]
                node_definition = single_call["node_definition_argument_info"]
                nodes.append({"name": node_name, "definition": node_definition})

            # Resolving the goto arguments of the Command objects
            for single_call in call_data:
                node_name = single_call["positional"][0]
                all_node_names = [node["name"] for node in nodes] + ["START", "END"]
                resolved_gotos = [
                    goto for goto in single_call["gotos"] if goto in all_node_names
                ]

                if len(resolved_gotos) > 1:
                    for resolved_goto in resolved_gotos:
                        conditional_edges.append(
                            {
                                "resolved": True,
                                "start_node": node_name,
                                "end_node": resolved_goto,
                            }
                        )
                elif len(resolved_gotos) == 1:
                    basic_edges.append(
                        {"start_node": node_name, "end_node": resolved_gotos[0]}
                    )

        if call_records.get("add_edge", False):
            all_node_names = [node["name"] for node in nodes] + ["START", "END"]
            call_data = call_records.get("add_edge")
            for single_call in call_data:
                nodes_in_edge = []
                # Since the call always contains two node names, we just add names from positional and keyword arguments (in this exact order)
                for node_name in single_call["positional"]:
                    nodes_in_edge.append(node_name)
                for _, node_name in single_call["keyword"].items():
                    nodes_in_edge.append(node_name)

                if (
                    nodes_in_edge[0] in all_node_names
                    and nodes_in_edge[1] in all_node_names
                ):
                    basic_edges.append(
                        {"start_node": nodes_in_edge[0], "end_node": nodes_in_edge[1]}
                    )

        if call_records.get("add_conditional_edges", False):
            all_node_names = [node["name"] for node in nodes] + ["START", "END"]
            call_data = call_records.get("add_conditional_edges")
            for single_call in call_data:
                # Resolving arguments to find the source node
                arguments = []
                for argument in single_call["positional"]:
                    arguments.append(argument)
                for _, argument in single_call["keyword"].items():
                    arguments.append(argument)

                if single_call.get("path", False):
                    if single_call["path"].get("function_returns", False):
                        for end_node in single_call["path"].get("function_returns"):
                            if (
                                arguments[0] in all_node_names
                                and end_node in all_node_names
                            ):
                                conditional_edges.append(
                                    {
                                        "resolved": True,
                                        "start_node": arguments[0],
                                        "end_node": end_node,
                                    }
                                )
                elif single_call.get("path_map", False):
                    if single_call["path_map"].get("list_values", False):
                        for end_node in single_call["path_map"].get("list_values"):
                            if (
                                arguments[0] in all_node_names
                                and end_node in all_node_names
                            ):
                                conditional_edges.append(
                                    {
                                        "resolved": True,
                                        "start_node": arguments[0],
                                        "end_node": end_node,
                                    }
                                )
                    elif single_call["path_map"].get("dict_values", False):
                        for end_node in single_call["path_map"].get("dict_values"):
                            if (
                                arguments[0] in all_node_names
                                and end_node in all_node_names
                            ):
                                conditional_edges.append(
                                    {
                                        "resolved": True,
                                        "start_node": arguments[0],
                                        "end_node": end_node,
                                    }
                                )
        if call_records.get("set_entry_point", False):
            call_data = call_records.get("set_entry_point")
            entrypoints = []
            for single_call in call_data:
                for node_name in single_call["positional"]:
                    entrypoints.append(node_name)
                for _, node_name in single_call["keyword"].items():
                    entrypoints.append(node_name)

            for node_name in entrypoints:
                basic_edges.append({"start_node": "START", "end_node": node_name})
        graphs.append(
            {
                "graph_name": graph,
                "graph_file_path": call_records["filepath"],
                "graph_info": {
                    "nodes": nodes,
                    "basic_edges": basic_edges,
                    "conditional_edges": conditional_edges,
                },
            }
        )
    return graphs
