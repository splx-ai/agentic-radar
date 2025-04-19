import json
from typing import List, Tuple

import importlib_resources as resources

from ...graph import (
    EdgeDefinition,
    NodeDefinition,
    NodeType,
)
from .models import N8nConnection, N8nNode


def convert_nodes(
    n8n_nodes: List[N8nNode],
    use_n8n_positions: bool = False
) -> Tuple[List[NodeDefinition], List[NodeDefinition]]:
    nodes = []
    tools = []
    n8n_node_types_file = resources.files(__package__) / "n8n_node_types.json"
    with n8n_node_types_file.open("r") as f:
        n8n_node_types_dict = json.load(f)

    for n8n_node in n8n_nodes:
        type = None
        if n8n_node.type in n8n_node_types_dict:
            type = n8n_node_types_dict.get(n8n_node.type)
        elif n8n_node.type.strip("tool") in n8n_node_types_dict:
            type = n8n_node_types_dict.get(n8n_node.type.strip("tool"))

        # Extract position coordinates if available
        position_x = None
        position_y = None
        if n8n_node.position and len(n8n_node.position) >= 2 and use_n8n_positions:
            # Scale down position values to reduce distance between nodes
            position_x = n8n_node.position[0] / 5
            position_y = n8n_node.position[1] / 5
        elif n8n_node.position and len(n8n_node.position) >= 2:
            # When not using scaled positions, still store the original positions
            position_x = None
            position_y = None

        if type:
            if type.get("tool_type", False):
                nodes.append(
                    NodeDefinition(
                        type=NodeType.TOOL,
                        name=n8n_node.name,
                        label=n8n_node.name,
                        category=type.get("tool_type"),
                        position_x=position_x,
                        position_y=position_y
                    )
                )

                tools.append(
                    NodeDefinition(
                        type=NodeType.TOOL,
                        name=n8n_node.name,
                        label=n8n_node.name,
                        category=type.get("tool_type"),
                        position_x=position_x,
                        position_y=position_y
                    )
                )
            else:
                nodes.append(
                    NodeDefinition(
                        type=type.get("node_type"),
                        name=n8n_node.name,
                        label=n8n_node.name,
                        position_x=position_x,
                        position_y=position_y
                    )
                )
        else:
            # For any node type not found in the dictionary, create a basic node
            nodes.append(
                NodeDefinition(
                    type=NodeType.BASIC,
                    name=n8n_node.name,
                    label=n8n_node.name,
                    position_x=position_x,
                    position_y=position_y
                )
            )

    return nodes, tools


def convert_connections(n8n_connections: List[N8nConnection]) -> List[EdgeDefinition]:
    edges = []
    for n8n_connection in n8n_connections:
        edges.append(
            EdgeDefinition(start=n8n_connection.start_node, end=n8n_connection.end_node)
        )

    return edges
