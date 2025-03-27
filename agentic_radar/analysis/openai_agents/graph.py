from agentic_radar.analysis.openai_agents.models import Agent, Tool
from agentic_radar.graph import (
    EdgeDefinition,
    GraphDefinition,
    NodeDefinition,
    NodeType,
    ToolType,
)


def create_graph_definition(
    graph_name: str,
    agent_assignments: dict[str, Agent],
    tool_categories: dict[str, ToolType],
) -> GraphDefinition:
    nodes = []
    edges = []
    tools = []

    for agent in agent_assignments.values():
        nodes.append(_get_agent_node(agent))

    for agent in agent_assignments.values():
        for tool in agent.tools:
            category = tool_categories.get(tool.name, ToolType.DEFAULT)
            tool_node = _get_tool_node(tool, category)
            nodes.append(tool_node)
            tools.append(tool_node.model_copy(deep=True))
            edges.append(
                EdgeDefinition(start=agent.name, end=tool.name, condition="tool_call")
            )
            edges.append(EdgeDefinition(start=tool.name, end=agent.name))

        for handoff in agent.handoffs:
            if handoff not in agent_assignments:
                print(
                    f"Warning while processing agent {agent.name}: handoff agent {handoff} not found, skipping..."
                )
            else:
                handoff_agent = agent_assignments[handoff]
                edge_condition = "handoff" if len(agent.handoffs) > 1 else None
                edges.append(
                    EdgeDefinition(
                        start=agent.name,
                        end=handoff_agent.name,
                        condition=edge_condition,
                    )
                )

    nodes, edges = _add_start_end_nodes(nodes=nodes, edges=edges)
    return GraphDefinition(name=graph_name, nodes=nodes, edges=edges, tools=tools)


def _get_agent_node(agent: Agent) -> NodeDefinition:
    return NodeDefinition(type=NodeType.AGENT, name=agent.name, label=agent.name)


def _get_tool_node(tool: Tool, category: ToolType) -> NodeDefinition:
    return NodeDefinition(
        type=NodeType.CUSTOM_TOOL if tool.custom else NodeType.TOOL,
        name=tool.name,
        description=tool.description,
        label=tool.name,
        category=category,
    )


def _add_start_end_nodes(nodes: list[NodeDefinition], edges: list[EdgeDefinition]):
    """
    Add start and end nodes to the graph by:
    1. Creating a start node and connecting it to agents with no incoming agent edges
    2. Creating an end node and connecting agents with no outgoing agent edges to it

    Args:
        nodes (list[NodeDefinition]): List of nodes to modify
        edges (list[EdgeDefinition]): List of edges to modify

    Returns:
        tuple[list[NodeDefinition], list[EdgeDefinition]]: Updated nodes and edges
    """
    # Create start and end nodes
    start_node = NodeDefinition(type=NodeType.BASIC, name="start", label="Start")
    end_node = NodeDefinition(type=NodeType.BASIC, name="end", label="End")

    # Find agent node names
    agent_nodes = {node.name for node in nodes if node.node_type == NodeType.AGENT}

    # Track incoming and outgoing agent edges for each node
    incoming_agent_edges: dict[str, int] = {}
    outgoing_agent_edges: dict[str, int] = {}

    # Populate agent edge tracking dictionaries
    for edge in edges:
        if edge.start in agent_nodes and edge.end in agent_nodes:
            incoming_agent_edges[edge.end] = incoming_agent_edges.get(edge.end, 0) + 1
            outgoing_agent_edges[edge.start] = (
                outgoing_agent_edges.get(edge.start, 0) + 1
            )

    # Add start node connections for agents with no incoming agent edges
    for node_name in agent_nodes:
        if incoming_agent_edges.get(node_name, 0) == 0:
            edges.append(EdgeDefinition(start="start", end=node_name))

    # Add end node connections for agents with no outgoing agent edges
    for node_name in agent_nodes:
        if outgoing_agent_edges.get(node_name, 0) == 0:
            edges.append(EdgeDefinition(start=node_name, end="end"))

    # Add start and end nodes to the node list
    nodes.extend([start_node, end_node])

    # Return updated nodes and edges
    return nodes, edges
