from pathlib import Path

from agentic_radar.analysis.analyze import Analyzer
from agentic_radar.analysis.openai_agents.graph import create_graph_definition
from agentic_radar.analysis.openai_agents.parsing import (
    collect_agent_assignments,
    collect_tool_assignments,
    load_predefined_tools,
)
from agentic_radar.analysis.openai_agents.tool_categorizer.categorizer import (
    load_tool_categories,
)
from agentic_radar.graph import GraphDefinition


class OpenAIAgentsAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def analyze(self, root_directory: str) -> GraphDefinition:
        tool_assignments = collect_tool_assignments(root_directory)
        predefined_tools = load_predefined_tools()
        agent_assignments = collect_agent_assignments(
            root_dir=root_directory,
            tool_assignments=tool_assignments,
            predefined_tools=predefined_tools,
        )
        tool_categories = load_tool_categories()
        graph_definition = create_graph_definition(
            graph_name=Path(root_directory).name,
            agent_assignments=agent_assignments,
            tool_categories=tool_categories,
        )
        return graph_definition
