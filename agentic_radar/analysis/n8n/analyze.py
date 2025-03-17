from pathlib import Path
import os
import json
from typing import Tuple, List

from ...analysis.analyze import Analyzer
from ...graph import EdgeDefinition as Edge
from ...graph import GraphDefinition
from ...graph import NodeDefinition as Node
from ...graph import NodeType, ToolType

from .converter import (
    convert_nodes,
    convert_connections
)

from .parsing import (
    parse_n8n_nodes,
    parse_n8n_connections
)
from .models import (
    N8nNode,
    N8nConnection
)


class N8nAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def parse_n8n_configs(self, root_directory: str) -> Tuple[List[N8nNode], List[N8nConnection]]:
        n8n_nodes = []
        n8n_connections = []
        workflow_name = None
        for root, _, files in os.walk(root_directory):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding = "utf-8") as f:
                        config = json.load(f)
                        if config.get("nodes", False) and config.get("connections", False):
                            n8n_nodes.extend(parse_n8n_nodes(config.get("nodes")))
                            n8n_connections.extend(parse_n8n_connections(config.get("connections")))
                            if config.get("name", False):
                                workflow_name = config.get("name")
                            else:
                                workflow_name = file.strip(".json")

        return n8n_nodes, n8n_connections, workflow_name

    def analyze(self, root_directory: str) -> GraphDefinition:
        
        n8n_nodes, n8n_connections, workflow_name = self.parse_n8n_configs(root_directory)

        nodes, tools = convert_nodes(n8n_nodes)
        edges = convert_connections(n8n_connections)

        return GraphDefinition(
            name=workflow_name, nodes=nodes, edges=edges, tools=tools
        )