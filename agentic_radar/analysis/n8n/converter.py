from typing import List, Tuple

from models import (
    N8nNode,
    N8nConnection
)

from ...graph import (
    EdgeDefinition,
    NodeDefinition,
    NodeType,
    ToolType
)

def convert_nodes(n8n_nodes: List[N8nNode]) -> Tuple[List[N8nNode], List[N8nNode]]:
    for n8n_node in n8n_nodes:
        pass


def convert_connections(n8n_connections: List[N8nConnection]) -> List[EdgeDefinition]:
    edges = []
    for n8n_connection in n8n_connections:
        edges.append(
            EdgeDefinition(
                start = n8n_connection.start_node,
                end = n8n_connection.end_node
            )
        )

    return edges