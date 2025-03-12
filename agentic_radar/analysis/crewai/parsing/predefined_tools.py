import ast
import os

from ..models.tool import CrewAITool
from ..tool_descriptions import get_crewai_tools_descriptions


class PredefinedToolsCollector(ast.NodeVisitor):
    CREWAI_TOOLS_MODULE = "crewai_tools"

    def __init__(self):
        self.known_tool_aliases = set()
        self.predefined_tool_vars = {}

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
                self.predefined_tool_vars[target.id] = node.value.func.id
            elif isinstance(node.value, ast.Attribute):
                if (
                    self.CREWAI_TOOLS_MODULE in node.value
                    and node.value.attr in self.known_tool_aliases
                ):
                    self.predefined_tool_vars[target.id] = node.value.attr

    def collect(self, root_dir: str) -> tuple[set, dict]:
        """Parses all Python modules in the given directory and collects predefined tools.

        Args:
            root_dir (str): Path to the codebase directory

        Returns:
            tuple[set[str], dict[str, CrewAITool]]: A tuple containing a set of known tool aliases and a dictionary of predefined tool variables
        """

        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as file:
                        code = file.read()
                        tree = ast.parse(code)
                        self.visit(tree)

        # Add descriptions and wrap tools inside CrewAITool instances 
        tools_descriptions = get_crewai_tools_descriptions()
        predefined_tool_vars = {
            var_name: CrewAITool(
                name=tool_name,
                custom=False,
                description=tools_descriptions.get(tool_name, ""),
            )
            for var_name, tool_name in self.predefined_tool_vars.items()
        }

        return self.known_tool_aliases, predefined_tool_vars
