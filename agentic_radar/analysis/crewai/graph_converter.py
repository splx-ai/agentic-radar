from agentic_radar.analysis.crewai.models import (
    CrewAIAgent,
    CrewAIGraph,
    CrewAINodeType,
)
from agentic_radar.analysis.crewai.prompt import build_system_prompt
from agentic_radar.analysis.crewai.tool_categorizer import categorize_tool
from agentic_radar.graph import (
    Agent as ReportAgent,
)
from agentic_radar.graph import (
    EdgeDefinition,
    GraphDefinition,
    NodeDefinition,
    NodeType,
    ToolType,
)


def convert_graph(
    crewai_graph: CrewAIGraph, agents: dict[str, CrewAIAgent]
) -> GraphDefinition:
    """Convert CrewAI Graph to GraphDefinition."""
    nodes = []
    edges = []
    tools = []

    for node in crewai_graph.nodes:
        if node.type == CrewAINodeType.AGENT:
            node_type = NodeType.AGENT
        elif node.type == CrewAINodeType.TOOL:
            node_type = NodeType.TOOL
        elif node.type == CrewAINodeType.CUSTOM_TOOL:
            node_type = NodeType.CUSTOM_TOOL
        elif node.type == CrewAINodeType.BASIC:
            node_type = NodeType.BASIC
        else:
            node_type = NodeType.DEFAULT

        category = None
        if node_type == NodeType.TOOL:
            category = categorize_tool(node.name)
        elif node_type == NodeType.CUSTOM_TOOL:
            category = ToolType.DEFAULT

        output_node = NodeDefinition(
            type=node_type,
            name=node.name,
            label=node.name,
            category=category,
            description=node.description,
        )

        nodes.append(output_node.model_copy(deep=True))

        if node.type == CrewAINodeType.TOOL or node.type == CrewAINodeType.CUSTOM_TOOL:
            tools.append(output_node.model_copy(deep=True))

    for edge in crewai_graph.edges:
        edges.append(
            EdgeDefinition(
                start=edge.start_node,
                end=edge.end_node,
                condition=edge.condition,
            )
        )

    # Add Agent metadata
    report_agents = []
    try:
        for agent_name, agent in agents.items():
            if crewai_graph.is_agent_in_graph(agent_name):
                system_prompt = build_system_prompt(agent)
                report_agent = ReportAgent(
                    name=agent_name, llm=agent.llm, system_prompt=system_prompt
                )
                report_agents.append(report_agent)
    except ImportError:
        print(
            "CrewAI package is not installed. Skipping agent metadata. Install the package to use this feature."
        )

    return GraphDefinition(
        name=crewai_graph.name,
        nodes=nodes,
        edges=edges,
        agents=report_agents,
        tools=tools,
    )
