from agentic_radar.graph import GraphDefinition, NodeDefinition, EdgeDefinition, NodeType, ToolType
from agentic_radar.analysis.crewai.models import CrewAIGraph, CrewAINodeType
from agentic_radar.analysis.crewai.tool_categorizer import categorize_tool

def convert_graph(crewai_graph: CrewAIGraph) -> GraphDefinition:
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
            node_type=node_type,
            name=node.name,
            label=node.name,
            category=category,
            description=node.description
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

    return GraphDefinition(name=crewai_graph.name, nodes=nodes, edges=edges, tools=tools)
