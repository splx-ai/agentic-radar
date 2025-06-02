import ast
from typing import Union

from ...ast_utils import (
    find_decorator_by_name,
    get_simple_identifier_name,
    get_string_keyword_arg,
    is_function_call,
    is_simple_identifier,
)
from ...utils import walk_python_files
from ..models import Tool


class ToolsVisitor(ast.NodeVisitor):
    TOOL_DECORATOR_NAME = "function_tool"
    TOOL_CONSTRUCTOR_NAME = "FunctionTool"

    def __init__(self) -> None:
        super().__init__()
        self.tool_assignments: dict[str, Tool] = {}

    def visit_FunctionDef(self, node):
        self._visit_any_function_def(node)

    def visit_AsyncFunctionDef(self, node):
        self._visit_any_function_def(node)

    def visit_Assign(self, node):
        """Tracks cases like:
        tool = FunctionTool(name=mytool, description=mydescription)
        """
        if not is_function_call(node.value, self.TOOL_CONSTRUCTOR_NAME):
            return

        try:
            tool_name = get_string_keyword_arg(node.value, "name")
        except (ValueError, TypeError) as e:
            print(
                f"Failed to read tool name in {self.TOOL_CONSTRUCTOR_NAME} constructor. Error: {e}"
            )
            return

        try:
            tool_description = get_string_keyword_arg(node.value, "description")
        except (ValueError, TypeError):
            tool_description = ""

        tool = Tool(name=tool_name, custom=True, description=tool_description)
        for target in node.targets:
            if not is_simple_identifier(target):
                continue

            target_name = get_simple_identifier_name(target)
            self.tool_assignments[target_name] = tool

    def _visit_any_function_def(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ):
        tool_decorator = find_decorator_by_name(node, self.TOOL_DECORATOR_NAME)
        if not tool_decorator:
            return

        tool_name = node.name
        if isinstance(tool_decorator, ast.Call):
            try:
                tool_name_override = get_string_keyword_arg(
                    tool_decorator, "name_override"
                )
                if tool_name_override:
                    tool_name = tool_name_override
            except (ValueError, TypeError):
                pass
        description = ast.get_docstring(node) or ""
        tool = Tool(name=tool_name, custom=True, description=description)
        self.tool_assignments[node.name] = tool


def collect_tool_assignments(root_dir: str) -> dict[str, Tool]:
    all_tool_assignments: dict[str, Tool] = {}
    for file in walk_python_files(root_dir):
        with open(file, "r") as f:
            try:
                tree = ast.parse(f.read())
            except Exception as e:
                print(f"Cannot parse Python module: {file}. Error: {e}")
                continue
            tools_visitor = ToolsVisitor()
            tools_visitor.visit(tree)
            all_tool_assignments |= tools_visitor.tool_assignments

    return all_tool_assignments
