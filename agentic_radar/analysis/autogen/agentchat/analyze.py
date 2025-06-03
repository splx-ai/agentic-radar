from pathlib import Path

from agentic_radar.analysis.analyze import Analyzer
from agentic_radar.analysis.ast_utils import walk_and_parse_python_files
from agentic_radar.graph import GraphDefinition

from .graph import create_graph_definition
from .parse import (
    find_agent_assignments,
    find_all_functions,
    find_function_tool_assignments,
    find_model_client_assignments,
    find_model_client_imports,
    find_teams,
)


class AutogenAgentChatAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def analyze(self, root_directory: str) -> GraphDefinition:
        trees = [tree for _, tree in walk_and_parse_python_files(root_directory)]
        all_functions = find_all_functions(trees)
        model_imports = find_model_client_imports(trees)
        model_clients = find_model_client_assignments(trees, model_imports)
        function_tools = find_function_tool_assignments(trees, all_functions)
        agent_assignments = find_agent_assignments(
            trees, model_clients, function_tools, all_functions
        )
        teams = find_teams(trees, agent_assignments)
        graph = create_graph_definition(Path(root_directory).name, teams)

        return graph
