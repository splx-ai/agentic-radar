import ast
from typing import Union

from ...ast_utils import (
    find_decorator_by_name,
)
from ...utils import walk_python_files
from ..models import Agent, Guardrail


class GuardrailsVisitor(ast.NodeVisitor):
    GUARDRAIL_DECORATOR_NAMES = ["input_guardrail", "output_guardrail"]
    GUARDRAIL_CLASS_NAMES = ["InputGuardrail", "OutputGuardrail"]

    def __init__(self) -> None:
        super().__init__()
        self.guardrails: dict[str, Guardrail] = {}
        self.functions: dict[str, Union[ast.FunctionDef, ast.AsyncFunctionDef]] = {}

    def visit_FunctionDef(self, node):
        self.functions[node.name] = node
        self._visit_any_function_def(node)

    def visit_AsyncFunctionDef(self, node):
        self.functions[node.name] = node
        self._visit_any_function_def(node)

    def visit_Assign(self, node):
        """Tracks cases like:
        guardrail = InputGuardrail(guardrail_function=function, name=guardrail_name)
        """
        if isinstance(node.value, ast.Call):
            call = node.value

            if (
                isinstance(call.func, ast.Name)
                and call.func.id in self.GUARDRAIL_CLASS_NAMES
            ):
                class_name = call.func.id

                guardrail_function_name = None
                for kw in call.keywords:
                    if kw.arg == "guardrail_function":
                        if isinstance(kw.value, ast.Name):
                            guardrail_function_name = kw.value.id
                        elif isinstance(kw.value, ast.Attribute):
                            guardrail_function_name = kw.value.attr  # for something like module.guardrail_fn BUT SEE IF WE WANT THIS EVEN

                if len(node.targets) > 0 and isinstance(node.targets[0], ast.Name):
                    guardrail_variable_name = node.targets[0].id
                    self.guardrails[guardrail_variable_name] = Guardrail(
                        name=guardrail_variable_name,
                        placement="input"
                        if class_name == self.GUARDRAIL_CLASS_NAMES[0]
                        else "output",
                        uses_agent=False,
                        guardrail_function_name=guardrail_function_name,
                        _guardrail_function_def=None,
                        agent_instructions=None,
                    )

    def _visit_any_function_def(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ):
        input_guardrail_decorator = find_decorator_by_name(
            node, self.GUARDRAIL_DECORATOR_NAMES[0]
        )
        output_guardrail_decorator = find_decorator_by_name(
            node, self.GUARDRAIL_DECORATOR_NAMES[1]
        )

        if input_guardrail_decorator is None and output_guardrail_decorator is None:
            return

        guardrail_name = node.name

        guardrail = Guardrail(
            name=guardrail_name,
            placement="input" if input_guardrail_decorator is not None else "output",
            uses_agent=False,
            guardrail_function_name=guardrail_name,
            agent_instructions=None,
        )

        guardrail._guardrail_function_def = node
        self.guardrails[guardrail_name] = guardrail


def analyze_guardrail(
    guardrail_name: str,
    guardrail: Guardrail,
    functions: dict[str, Union[ast.FunctionDef, ast.AsyncFunctionDef]],
    agent_assignments: dict[str, Agent],
) -> None:
    # Check if the guardrail function has Runner.run in it, as this indicates that an agent is used
    class RunnerCallVisitor(ast.NodeVisitor):
        def __init__(self):
            self.found = False
            self.starting_agent = None

        def check_call(self, call: ast.Call):
            if isinstance(call.func, ast.Attribute):
                if (
                    isinstance(call.func.value, ast.Name)
                    and call.func.value.id == "Runner"
                    and call.func.attr == "run"
                ):
                    if call.args:
                        self.found = True
                        first_arg = call.args[0]
                        if isinstance(first_arg, ast.Name):
                            self.starting_agent = first_arg.id

        def visit_Assign(self, node: ast.Assign):
            if isinstance(node.value, ast.Await) and isinstance(
                node.value.value, ast.Call
            ):
                self.check_call(node.value.value)
            self.generic_visit(node)

        def visit_Expr(self, node: ast.Expr):
            if isinstance(node.value, ast.Await) and isinstance(
                node.value.value, ast.Call
            ):
                self.check_call(node.value.value)
            self.generic_visit(node)

    if guardrail._guardrail_function_def is None:
        guardrail._guardrail_function_def = functions[guardrail.guardrail_function_name]

    visitor = RunnerCallVisitor()
    visitor.visit(guardrail._guardrail_function_def)

    if visitor.found:
        guardrail.uses_agent = True
        if visitor.starting_agent in agent_assignments.keys():
            guardrail.agent_instructions = agent_assignments[
                visitor.starting_agent
            ].instructions
            guardrail.agent_name = visitor.starting_agent
            agent_assignments[visitor.starting_agent].is_guardrail = True
        else:
            print("Oops, failed to find agent")


def collect_guardrails(
    root_dir: str, agent_assignments: dict[str, Agent]
) -> dict[str, Guardrail]:
    all_guardrails: dict[str, Guardrail] = {}
    for file in walk_python_files(root_dir):
        with open(file, "r") as f:
            try:
                tree = ast.parse(f.read())
            except Exception as e:
                print(f"Cannot parse Python module: {file}. Error: {e}")
                continue
            guardrails_visitor = GuardrailsVisitor()
            guardrails_visitor.visit(tree)
            for guardrail_name, guardrail in guardrails_visitor.guardrails.items():
                analyze_guardrail(
                    guardrail_name,
                    guardrail,
                    guardrails_visitor.functions,
                    agent_assignments,
                )
            all_guardrails |= guardrails_visitor.guardrails

    return all_guardrails
