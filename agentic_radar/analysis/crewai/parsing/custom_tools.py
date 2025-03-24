import ast

from agentic_radar.analysis.crewai.models.tool import CrewAITool
from agentic_radar.analysis.utils import walk_python_files


class CustomToolsVisitor(ast.NodeVisitor):
    CREWAI_CUSTOM_TOOL_DECORATOR = "tool"
    CREWAI_CUSTOM_TOOL_BASE_CLASS = "BaseTool"

    def __init__(self) -> None:
        self.custom_tools: dict[str, CrewAITool] = {}

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


def collect_custom_tools(root_dir: str) -> dict[str, CrewAITool]:
    """Parses all Python modules in the given directory and collects custom tools.

    Args:
        root_dir (str): Path to the codebase directory

    Returns:
        dict[str, CrewAITool]: Dictionary mapping custom tool name to corresponding CrewAITool instance
    """

    custom_tools: dict[str, CrewAITool] = {}

    for file in walk_python_files(root_dir):
        with open(file, "r") as f:
            try:
                tree = ast.parse(f.read())
            except Exception as e:
                print(f"Cannot parse Python module: {file}. Error: {e}")
                continue
            custom_tools_visitor = CustomToolsVisitor()
            custom_tools_visitor.visit(tree)
            custom_tools |= custom_tools_visitor.custom_tools

    return custom_tools
