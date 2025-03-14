import ast
import os

from ..models.tool import CrewAITool


class CustomToolsCollector(ast.NodeVisitor):
    CREWAI_CUSTOM_TOOL_DECORATOR = "tool"
    CREWAI_CUSTOM_TOOL_BASE_CLASS = "BaseTool"

    def __init__(self):
        self.custom_tools = {}

    def visit_FunctionDef(self, node):
        """Track functions that define custom tools by using the 'tools(...)' decorator."""
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and decorator.func.id == self.CREWAI_CUSTOM_TOOL_DECORATOR
            ):
                tool_description = ast.get_docstring(node) or ""
                self.custom_tools[node.name] = CrewAITool(
                    name=node.name, custom=True, description=tool_description
                )

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Tracks classes that define custom tools by detectng the 'BaseTool' base class."""
        for base in node.bases:
            if (
                isinstance(base, ast.Name)
                and base.id == self.CREWAI_CUSTOM_TOOL_BASE_CLASS
                or isinstance(base, ast.Attribute)
                and base.attr == self.CREWAI_CUSTOM_TOOL_BASE_CLASS
            ):
                tool_description = ast.get_docstring(node) or ""
                self.custom_tools[node.name] = CrewAITool(
                    name=node.name, custom=True, description=tool_description
                )

        self.generic_visit(node)

    def collect(self, root_dir: str) -> set[str]:
        """Parses all Python modules in the given directory and collects custom tools.

        Args:
            root_dir (str): Path to the codebase directory

        Returns:
            dict[str, CrewAITool]: Dictionary mapping custom tool name to corresponding CrewAITool instance
        """

        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), "r") as f:
                        tree = ast.parse(f.read())
                        self.visit(tree)

        return self.custom_tools
