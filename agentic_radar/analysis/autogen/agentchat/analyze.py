from pathlib import Path

from agentic_radar.analysis.analyze import Analyzer
from agentic_radar.analysis.ast_utils import walk_and_parse_python_files
from agentic_radar.graph import GraphDefinition

from .graph import create_graph_definition
from .mcp import (
    find_listed_mcp_tool_adapters,
    find_server_params,
    find_single_mcp_tool_adapters,
)
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
        mcp_servers = find_server_params(trees)
        mcp_adapters_to_servers = find_single_mcp_tool_adapters(trees, mcp_servers)
        listed_mcp_tool_adapters = find_listed_mcp_tool_adapters(trees, mcp_servers)
        agent_assignments = find_agent_assignments(
            trees,
            model_clients,
            function_tools,
            all_functions,
            mcp_adapters_to_servers,
            listed_mcp_tool_adapters,
        )
        teams = find_teams(trees, agent_assignments)

        agents_with_team = set(
            [member.name for team in teams for member in team.members]
        )
        teamless_agents = [
            a for a in agent_assignments.values() if a.name not in agents_with_team
        ]
        graph = create_graph_definition(
            Path(root_directory).name, teams, teamless_agents
        )

        return graph
