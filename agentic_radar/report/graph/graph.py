import json
from typing import List

from pydantic import BaseModel

from agentic_radar.report.graph.edge import Edge
from agentic_radar.report.graph.node import Node


class Graph(BaseModel):
    nodes: List[Node] = []
    edges: List[Edge] = []

    def generate(self) -> str:
        # Convert to ForceGraph expected format
        # Create a mapping of node names to their index for ForceGraph
        node_names = {node.name: idx for idx, node in enumerate(self.nodes)}
        
        force_graph_data = {
            "nodes": [
                {
                    **node.model_dump(),
                    "id": node.name  # Ensure each node has an id
                }
                for node in self.nodes
            ],
            "links": [
                {
                    "source": edge.source,  # Use node name/id directly
                    "target": edge.target,  # ForceGraph will resolve these
                    "label": getattr(edge, 'condition', None)
                }
                for edge in self.edges
                if edge.source in node_names and edge.target in node_names  # Filter out edges to non-existent nodes
            ]
        }
        return json.dumps(force_graph_data)
