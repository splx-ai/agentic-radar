import json
import os
from typing import List, Tuple

from ...analysis.analyze import Analyzer
from ...graph import GraphDefinition
from .converter import convert_connections, convert_nodes
from .models import N8nConnection, N8nNode
from .parsing import parse_n8n_connections, parse_n8n_nodes


class N8nAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def parse_n8n_configs(
        self, root_directory: str
    ) -> Tuple[List[N8nNode], List[N8nConnection], str]:
        n8n_nodes = []
        n8n_connections = []
        workflow_name = ""
        for root, _, files in os.walk(root_directory):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                        if config.get("nodes", False) and config.get(
                            "connections", False
                        ):
                            n8n_nodes.extend(parse_n8n_nodes(config.get("nodes")))
                            n8n_connections.extend(
                                parse_n8n_connections(config.get("connections"))
                            )
                            if config.get("name", False):
                                workflow_name = config.get("name")
                            else:
                                workflow_name = file.strip(".json")

        return n8n_nodes, n8n_connections, workflow_name

    def analyze(self, root_directory: str) -> GraphDefinition:
        n8n_nodes, n8n_connections, workflow_name = self.parse_n8n_configs(
            root_directory
        )

        nodes, tools = convert_nodes(n8n_nodes)
        edges = convert_connections(n8n_connections)

        return GraphDefinition(
            name=workflow_name, nodes=nodes, edges=edges, tools=tools
        )
