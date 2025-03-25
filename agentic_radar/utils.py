import html

from agentic_radar.graph import GraphDefinition


def sanitize_text(text: str) -> str:
    return html.escape(text)


def sanitize_graph(graph: GraphDefinition) -> None:
    nodes = graph.nodes
    edges = graph.edges
    tools = graph.tools

    for node in nodes:
        if node.name is not None:
            node.name = sanitize_text(node.name)
        if node.description is not None:
            node.description = sanitize_text(node.description)
        if node.label is not None:
            node.label = sanitize_text(node.label)
    for edge in edges:
        if edge.start is not None:
            edge.start = sanitize_text(edge.start)
        if edge.end is not None:
            edge.end = sanitize_text(edge.end)

    for tool in tools:
        if tool.name is not None:
            tool.name = sanitize_text(tool.name)
        if tool.description is not None:
            tool.description = sanitize_text(tool.description)
        if tool.label is not None:
            tool.label = sanitize_text(tool.label)
