from pathlib import Path
import os
import json
from typing import Tuple, List

from ...analysis.analyze import Analyzer
from ...graph import EdgeDefinition as Edge
from ...graph import GraphDefinition
from ...graph import NodeDefinition as Node
from ...graph import NodeType, ToolType

from converter import (
    convert_nodes,
    convert_connections
)

from parsing import (
    parse_n8n_nodes,
    parse_n8n_connections
)
from models import (
    N8nNode,
    N8nConnection
)


class N8nAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def parse_n8n_configs(self, root_directory: str) -> Tuple[List[N8nNode], List[N8nConnection]]:
        n8n_nodes = []
        n8n_connections = []
        for root, _, files in os.walk(root_directory):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as file:
                        config = json.load(file)
                        if config.get("nodes", False):
                            n8n_nodes.extend(parse_n8n_nodes(config.get("nodes")))
                        
                        if config.get("connections", False):
                            n8n_connections.extend(parse_n8n_connections(config.get("connections")))

        return n8n_nodes, n8n_connections

    def analyze(self, root_directory: str) -> GraphDefinition:
        
        n8n_nodes, n8n_connections = self.parse_n8n_configs(root_directory)

        nodes, tools = convert_nodes(n8n_nodes)
        edges = convert_connections(n8n_connections)

        return GraphDefinition(
            name=Path(root_directory).name, nodes=nodes, edges=edges, tools=tools
        )