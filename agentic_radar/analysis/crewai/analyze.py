from pathlib import Path

from agentic_radar.analysis.analyze import Analyzer
from agentic_radar.analysis.crewai.crew_process import infer_agent_connections
from agentic_radar.analysis.crewai.graph_converter import convert_graph
from agentic_radar.analysis.crewai.models import CrewAIAgent, CrewAIGraph
from agentic_radar.analysis.crewai.parsing import (
    collect_agents,
    collect_crews,
    collect_custom_tools,
    collect_predefined_tools,
    collect_tasks,
)
from agentic_radar.graph import GraphDefinition


class CrewAIAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def _parse_agents_and_tools(self, root_directory: str) -> dict[str, CrewAIAgent]:
        """Parse agents and their tools from the CrewAI codebase."""
        known_tool_aliases, predefined_tools = collect_predefined_tools(root_directory)
        custom_tools = collect_custom_tools(root_directory)
        agents = collect_agents(
            root_dir=root_directory,
            known_tool_aliases=known_tool_aliases,
            predefined_tools=predefined_tools,
            custom_tools=custom_tools,
        )
        return agents

    def _parse_agent_connections(self, root_directory: str, agents: set[str]):
        task_agent_mapping = collect_tasks(root_dir=root_directory, agents=agents)
        crew_task_mapping, crew_process_mapping = collect_crews(
            root_dir=root_directory, tasks=set(task_agent_mapping.keys())
        )
        agent_connections, start_agents, end_agents = infer_agent_connections(
            task_agent_mapping, crew_task_mapping, crew_process_mapping
        )
        return agent_connections, start_agents, end_agents

    def analyze(self, root_directory: str) -> GraphDefinition:
        """Analyze the CrewAI codebase and return the graph."""
        agents = self._parse_agents_and_tools(root_directory)
        agent_connections, start_agents, end_agents = self._parse_agent_connections(
            root_directory=root_directory, agents=set(agents.keys())
        )

        crewai_graph = CrewAIGraph(name=Path(root_directory).name)

        all_agents = set(agent_connections.keys()).union(*agent_connections.values())
        crewai_graph.create_agents(all_agents)
        crewai_graph.connect_agents(agent_connections)
        crewai_graph.add_start_end_nodes(start_agents, end_agents)

        for agent_name, agent in agents.items():
            if crewai_graph.is_agent_in_graph(agent_name):
                crewai_graph.create_tools(agent.tools)
                crewai_graph.connect_agent_to_tools(agent_name, agent.tools)

        graph = convert_graph(crewai_graph, agents)

        return graph
