import ast
import json
import os
from typing import Dict, Tuple, Union


def get_source_from_file(filepath: str) -> str:
    """
    Return the source code from a .py or .ipynb file as a single string.
    """
    if filepath.endswith(".py"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    elif filepath.endswith(".ipynb"):
        with open(filepath, "r", encoding="utf-8") as f:
            notebook = json.load(f)
            source = ""
            for cell in notebook.get("cells", []):
                if cell.get("cell_type") == "code":
                    if isinstance(cell["source"], list):
                        source += "".join(cell["source"])
                    else:
                        source += cell["source"]
            return source
    else:
        raise ValueError(
            f"Unsupported file type: {filepath}. Only .py and .ipynb are supported."
        )


def build_global_registry(
    root_dir: str,
) -> Tuple[
    Dict[str, Union[ast.FunctionDef, ast.AsyncFunctionDef]],
    Dict[str, Union[ast.List, ast.Dict]],
]:
    """
    Recursively walk `root_dir`,
    parse each .py file to find top-level function defs and variable defs
    (that are lists or dicts).

    We'll store them in global_functions and global_variables with a fully
    qualified name
    """
    global_functions: Dict[str, Union[ast.FunctionDef, ast.AsyncFunctionDef]] = {}
    global_variables: Dict[str, Union[ast.List, ast.Dict]] = {}
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py") or filename.endswith(".ipynb"):
                fullpath = os.path.join(dirpath, filename)
                module_name = derive_module_name(dirpath, filename, root_dir)
                local_functions, local_variables = parse_for_top_level_defs(
                    fullpath, module_name
                )

                for function_name, function_def in local_functions.items():
                    global_functions[function_name] = function_def

                for variable_name, variable_def in local_variables.items():
                    global_variables[variable_name] = variable_def

    return global_functions, global_variables


def derive_module_name(dirpath: str, filename: str, root_dir: str) -> str:
    """
    Convert a file path into a dotted module name
    """

    rel_path = os.path.relpath(dirpath, root_dir)
    parts = []
    if rel_path != ".":
        parts = rel_path.split(os.sep)

    base_name = ""
    if filename.endswith(".py"):
        base_name = filename.removesuffix(".py")
    elif filename.endswith(".ipynb"):
        base_name = filename.removesuffix(".ipynb")
    parts.append(base_name)

    module_name = ".".join(parts)
    return module_name


def parse_for_top_level_defs(
    filepath: str, module_name: str
) -> Tuple[
    Dict[str, Union[ast.FunctionDef, ast.AsyncFunctionDef]],
    Dict[str, Union[ast.List, ast.Dict]],
]:
    """
    Parse one file, collecting top-level function definitions and
    top-level variable definitions (lists/dicts)
    """
    local_functions: Dict[str, Union[ast.FunctionDef, ast.AsyncFunctionDef]] = {}
    local_variables: Dict[str, Union[ast.List, ast.Dict]] = {}

    source = get_source_from_file(filepath)
    try:
        tree = ast.parse(source, filename=filepath)
    except Exception as e:
        print(f"Cannot parse Python module: {filepath}. Error: {e}")
        return local_functions, local_variables

    class TopLevelCollector(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef):
            fq_key = f"{module_name}.{node.name}"
            local_functions[fq_key] = node
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
            fq_key = f"{module_name}.{node.name}"
            local_functions[fq_key] = node
            self.generic_visit(node)

        def visit_Assign(self, node: ast.Assign):
            if hasattr(node, "parent") and isinstance(node.parent, ast.Module):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    var_name = node.targets[0].id
                    val = node.value
                    if isinstance(val, (ast.List, ast.Dict)):
                        fq_key = f"{module_name}.{var_name}"
                        local_variables[fq_key] = val
            self.generic_visit(node)

        def generic_visit(self, node):
            for child in ast.iter_child_nodes(node):
                child.parent = node
                self.visit(child)

    collector = TopLevelCollector()
    collector.visit(tree)

    return local_functions, local_variables
