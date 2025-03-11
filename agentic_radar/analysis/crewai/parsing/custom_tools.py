import ast
import os


class CustomToolsCollector(ast.NodeVisitor):
    CREWAI_CUSTOM_TOOL_DECORATOR = "tool"
    CREWAI_CUSTOM_TOOL_BASE_CLASS = "BaseTool"

    def __init__(self):
        self.custom_tool_names = set()

    def visit_FunctionDef(self, node):
        """Track functions that define custom tools by using the 'tools(...)' decorator."""
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and decorator.func.id == self.CREWAI_CUSTOM_TOOL_DECORATOR
            ):
                self.custom_tool_names.add(node.name)

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
                self.custom_tool_names.add(node.name)

        self.generic_visit(node)

    def collect(self, root_dir: str) -> set[str]:
        """Parses all Python modules in the given directory and collects custom tools.

        Args:
            root_dir (str): Path to the codebase directory

        Returns:
            set[str]: Set of custom tool names
        """

        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), "r") as f:
                        tree = ast.parse(f.read())
                        self.visit(tree)

        return self.custom_tool_names
