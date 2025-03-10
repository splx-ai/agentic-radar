from pathlib import Path

from agentic_radar.graph import GraphDefinition
from agentic_radar.analysis.analyze import Analyzer
from agentic_radar.analysis.crewai.graph_converter import convert_graph
from agentic_radar.analysis.crewai.crew_process import infer_agent_connections
from agentic_radar.analysis.crewai.models import CrewAIGraph, CrewAITool
from agentic_radar.analysis.crewai.parsing import (
    PredefinedToolsCollector,
    CustomToolsCollector,
    AgentsCollector,
    TasksCollector,
    CrewsCollector,
)


class CrewAIAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def _parse_agents_and_tools(
        self, root_directory: str
    ) -> dict[str, list[CrewAITool]]:
        """Parse agents and their tools from the CrewAI codebase."""
        known_tool_aliases, predefined_tool_vars = PredefinedToolsCollector().collect(
            root_directory
        )
        custom_tool_names = CustomToolsCollector().collect(root_directory)
        agents_collector = AgentsCollector(
            known_tool_aliases, predefined_tool_vars, custom_tool_names
        )
        agent_tool_mapping = agents_collector.collect(root_directory)
        return agent_tool_mapping

    def _parse_agent_connections(self, root_directory: str, agents: set[str]):
        tasks_collector = TasksCollector(agents)
        task_agent_mapping = tasks_collector.collect(root_directory)

        crews_collector = CrewsCollector(set(task_agent_mapping.keys()))
        crew_task_mapping, crew_process_mapping = crews_collector.collect(
            root_directory
        )

        agent_connections, start_agents, end_agents = infer_agent_connections(
            task_agent_mapping, crew_task_mapping, crew_process_mapping
        )
        return agent_connections, start_agents, end_agents 

    def analyze(self, root_directory: str) -> GraphDefinition:
        """Analyze the CrewAI codebase and return the graph."""
        agent_tool_mapping = self._parse_agents_and_tools(root_directory)
        agent_connections, start_agents, end_agents = self._parse_agent_connections(
            root_directory=root_directory, agents=set(agent_tool_mapping.keys())
        )

        crewai_graph = CrewAIGraph(name=Path(root_directory).name)

        all_agents = set(agent_connections.keys()).union(*agent_connections.values())
        crewai_graph.create_agents(all_agents)
        crewai_graph.connect_agents(agent_connections)
        crewai_graph.add_start_end_nodes(start_agents, end_agents)

        for agent, tools in agent_tool_mapping.items():
            if crewai_graph.is_agent_in_graph(agent):
                crewai_graph.create_tools(tools)
                crewai_graph.connect_agent_to_tools(agent, tools)

        graph = convert_graph(crewai_graph)
        return graph
