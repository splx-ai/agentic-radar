import json
from typing import Any, List, Tuple

import importlib_resources as resources

from ...graph import EdgeDefinition, NodeDefinition, NodeType, ToolType
from .models import N8nConnection, N8nNode


def convert_nodes(
    n8n_nodes: List[N8nNode],
) -> Tuple[List[NodeDefinition], List[NodeDefinition]]:
    nodes: list[NodeDefinition] = []
    tools: list[NodeDefinition] = []
    n8n_node_types_file = resources.files(__package__) / "n8n_node_types.json"
    with n8n_node_types_file.open("r") as f:
        n8n_node_types_dict = json.load(f)

    for n8n_node in n8n_nodes:
        node_type_data: dict[str, Any] | None = None
        if n8n_node.type in n8n_node_types_dict:
            node_type_data = n8n_node_types_dict.get(n8n_node.type)
        elif n8n_node.type.strip("tool") in n8n_node_types_dict:
            node_type_data = n8n_node_types_dict.get(n8n_node.type.strip("tool"))
        else:
            node_type_data = {"node_type": NodeType.BASIC}

        if node_type_data:
            node_type_value = node_type_data.get("node_type", NodeType.BASIC)
            if isinstance(node_type_value, NodeType):
                node_type = node_type_value
            else:
                try:
                    node_type = NodeType(node_type_value)
                except Exception:
                    node_type = NodeType.BASIC

            tool_type_value = node_type_data.get("tool_type")
            tool_category = (
                tool_type_value
                if isinstance(tool_type_value, ToolType)
                else ToolType(tool_type_value)
                if isinstance(tool_type_value, str)
                and tool_type_value in ToolType._value2member_map_
                else None
            )

            if tool_category:
                nodes.append(
                    NodeDefinition(
                        type=NodeType.TOOL,
                        name=n8n_node.name,
                        label=n8n_node.name,
                        category=tool_category,
                    )
                )

                tools.append(
                    NodeDefinition(
                        type=NodeType.TOOL,
                        name=n8n_node.name,
                        label=n8n_node.name,
                        category=tool_category,
                    )
                )
            else:
                description = (
                    json.dumps(n8n_node.parameters)
                    if node_type == NodeType.MCP_SERVER
                    else None
                )
                nodes.append(
                    NodeDefinition(
                        type=node_type,
                        name=n8n_node.name,
                        label=n8n_node.name,
                        description=description,
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
