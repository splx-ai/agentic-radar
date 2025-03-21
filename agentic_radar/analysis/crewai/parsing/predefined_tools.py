import ast

from agentic_radar.analysis.crewai.models.tool import CrewAITool
from agentic_radar.analysis.crewai.tool_descriptions import (
    get_crewai_tools_descriptions,
)
from agentic_radar.analysis.utils import walk_python_files


class PredefinedToolsVisitor(ast.NodeVisitor):
    CREWAI_TOOLS_MODULE = "crewai_tools"

    def __init__(self):
        self.known_tool_aliases: set[str] = set()
        self.predefined_tools: dict[str, str] = {}

    def visit_ImportFrom(self, node):
        """Track imports like 'from crewai_tools import FileReadTool'."""
        if node.module == self.CREWAI_TOOLS_MODULE:
            for alias in node.names:
                tool_name = alias.asname or alias.name
                self.known_tool_aliases.add(tool_name)

    def visit_Assign(self, node):
        """Tracks assigments like some_tool = FileReadTool()"""
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue

            if not isinstance(node.value, ast.Call):
                continue

            if (
                isinstance(node.value.func, ast.Name)
                and node.value.func.id in self.known_tool_aliases
            ):
                self.predefined_tools[target.id] = node.value.func.id
            elif isinstance(node.value, ast.Attribute):
                if (
                    self.CREWAI_TOOLS_MODULE in node.value
                    and node.value.attr in self.known_tool_aliases
                ):
                    self.predefined_tools[target.id] = node.value.attr


def collect_predefined_tools(root_dir: str) -> tuple[set, dict]:
    """Parses all Python modules in the given directory and collects predefined tools.

    Args:
        root_dir (str): Path to the codebase directory

    Returns:
        tuple[set[str], dict[str, CrewAITool]]: A tuple containing a set of known tool aliases and a dictionary of predefined tool variables
    """
    known_tool_aliases: set[str] = set()
    predefined_tools: dict[str, str] = {}

    for file in walk_python_files(root_dir):
        with open(file, "r") as f:
            try:
                tree = ast.parse(f.read())
            except Exception as e:
                print(f"Cannot parse Python module: {file}. Error: {e}")
                continue
            predefined_tools_visitor = PredefinedToolsVisitor()
            predefined_tools_visitor.visit(tree)
            known_tool_aliases |= predefined_tools_visitor.known_tool_aliases
            predefined_tools |= predefined_tools_visitor.predefined_tools

    # Add descriptions and wrap tools inside CrewAITool instances
    tools_descriptions = get_crewai_tools_descriptions()
    predefined_tools_with_descriptions = {
        var_name: CrewAITool(
            name=tool_name,
            custom=False,
            description=tools_descriptions.get(tool_name, ""),
        )
        for var_name, tool_name in predefined_tools.items()
    }

    return known_tool_aliases, predefined_tools_with_descriptions
