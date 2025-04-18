import json
import os
from typing import List, Tuple, Dict

from ...analysis.analyze import Analyzer
from ...graph import GraphDefinition
from .converter import convert_connections, convert_nodes
from .models import N8nConnection, N8nNode
from .parsing import parse_n8n_connections, parse_n8n_nodes


class N8nAnalyzer(Analyzer):
    def __init__(self, connected_only=False, langchain_only=False):
        super().__init__()
        self.connected_only = connected_only
        self.langchain_only = langchain_only

    def parse_n8n_config_file(
        self, file_path: str
    ) -> Tuple[List[N8nNode], List[N8nConnection], str]:
        n8n_nodes = []
        n8n_connections = []
        workflow_name = ""

        with open(file_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            if config.get("nodes", False) and config.get(
                "connections", False
            ):
                n8n_nodes = parse_n8n_nodes(config.get("nodes"))
                n8n_connections = parse_n8n_connections(config.get("connections"))
                if config.get("name", False):
                    workflow_name = config.get("name")
                else:
                    workflow_name = os.path.basename(file_path).strip(".json")

        return n8n_nodes, n8n_connections, workflow_name

    def has_langchain_nodes(self, n8n_nodes: List[N8nNode]) -> bool:
        """Check if any of the nodes are LangChain nodes."""
        for node in n8n_nodes:
            if "langchain" in node.type.lower():
                return True
        return False

    def analyze(self, root_directory: str) -> List[GraphDefinition]:
        workflow_graphs = []

        for root, _, files in os.walk(root_directory):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    n8n_nodes, n8n_connections, workflow_name = self.parse_n8n_config_file(file_path)

                    if n8n_nodes and n8n_connections:
                        # Skip workflows without connections if connected_only is True
                        if self.connected_only and not n8n_connections:
                            print(f"Skipping workflow '{workflow_name}' as it has no connections")
                            continue
                        
                        # Skip workflows without LangChain nodes if langchain_only is True
                        if self.langchain_only and not self.has_langchain_nodes(n8n_nodes):
                            print(f"Skipping workflow '{workflow_name}' as it has no LangChain nodes")
                            continue
                            
                        nodes, tools = convert_nodes(n8n_nodes)
                        edges = convert_connections(n8n_connections)

                        workflow_graphs.append(GraphDefinition(
                            name=workflow_name, nodes=nodes, edges=edges, tools=tools
                        ))

        return workflow_graphs
