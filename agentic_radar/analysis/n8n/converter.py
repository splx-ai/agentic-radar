from typing import List, Tuple
from importlib import resources
import json

from .models import (
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
    nodes = []
    tools = []
    n8n_node_types_file = resources.files(__package__) / "n8n_node_types.json"
    with open(n8n_node_types_file, "r") as f:
        n8n_node_types_dict = json.load(f)

    for n8n_node in n8n_nodes:
        type = None
        if n8n_node.type in n8n_node_types_dict:
            type = n8n_node_types_dict.get(n8n_node.type)
        elif n8n_node.type.strip("tool") in n8n_node_types_dict:
            type = n8n_node_types_dict.get(n8n_node.type.strip("tool"))

        if type:
            if type.get("tool_type", False):
                nodes.append(
                    NodeDefinition(
                        type = "tool",
                        name = n8n_node.name,
                        label = n8n_node.name,
                        category = type.get("tool_type")
                    )
                )

                tools.append(
                    NodeDefinition(
                        type = "tool",
                        name = n8n_node.name,
                        label = n8n_node.name,
                        category = type.get("tool_type")
                    )
                )
            else:
                nodes.append(
                    NodeDefinition(
                        type = type.get("node_type"),
                        name = n8n_node.name,
                        label = n8n_node.name
                    )
                )

    return nodes, tools    


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