from typing import Dict, List

from .models import (
    N8nNode,
    N8nConnection
)

def parse_n8n_nodes(nodes_list: List[Dict]) -> List[N8nNode]:
    n8n_nodes = []
    for node in nodes_list:
        n8n_nodes.append(
            N8nNode(
                id = node["id"],
                name = node["name"],
                type = node["type"].lower()
            )
        )

    return n8n_nodes

def parse_n8n_connections(connections_dict: Dict) -> List[N8nConnection]:
    n8n_connections = []
    for node, connection_types_dict in connections_dict.items():
        for connection_type, list_of_connection_lists in connection_types_dict.items():
            for list_of_connections in list_of_connection_lists:
                for connection in list_of_connections:
                    n8n_connections.append(
                        N8nConnection(
                            start_node = node,
                            end_node = connection["node"]
                        ))
                    
    return n8n_connections