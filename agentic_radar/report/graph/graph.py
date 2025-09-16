import json
from typing import List, Optional

from pydantic import BaseModel

from agentic_radar.report.graph.edge import Edge
from agentic_radar.report.graph.node import Node


class Graph(BaseModel):
    nodes: List[Node] = []
    edges: List[Edge] = []

    def generate(self, visualization: str = "force-graph") -> str:
        """
        Generate graph data in the specified visualization format.
        
        Args:
            visualization: The visualization library to target ("force-graph" or "vis-js")
            
        Returns:
            JSON string in the appropriate format
        """
        # Create a mapping of node names to their index
        node_names = {node.name: idx for idx, node in enumerate(self.nodes)}
        
        # Prepare node data
        nodes_data = [
            {
                **node.model_dump(),
                "id": node.name  # Ensure each node has an id
            }
            for node in self.nodes
        ]
        
        # Prepare edge/link data
        edges_data = [
            {
                "source": edge.source,  # Use node name/id directly
                "target": edge.target,  # Libraries will resolve these
                "label": getattr(edge, 'condition', None)
            }
            for edge in self.edges
            if edge.source in node_names and edge.target in node_names  # Filter out edges to non-existent nodes
        ]
        
        if visualization == "vis-js":
            # vis.js format uses "edges" key
            return self._generate_vis_js_format(nodes_data, edges_data)
        else:
            # ForceGraph format uses "links" key
            force_graph_data = {
                "nodes": nodes_data,
                "links": edges_data  # ForceGraph expects "links"
            }
            return json.dumps(force_graph_data)
    
    def _generate_vis_js_format(self, nodes_data: list, edges_data: list) -> str:
        """
        Generate vis.js compatible format.
        
        Args:
            nodes_data: List of node dictionaries
            edges_data: List of edge dictionaries
            
        Returns:
            JSON string in vis.js format
        """
        # vis.js expects different structure
        vis_nodes = []
        for i, node in enumerate(nodes_data):
            vis_node = {
                "id": node.get("id") or node.get("name"),
                "label": node.get("label") or node.get("name"),
                "title": node.get("description", ""),  # Tooltip on hover
                "group": node.get("type", "default"),  # For coloring
            }
            # Add image if available
            if node.get("image"):
                vis_node["image"] = node["image"]
                vis_node["shape"] = "image"
            vis_nodes.append(vis_node)
        
        # Transform edges to vis.js format
        vis_edges = []
        for edge in edges_data:
            vis_edge = {
                "from": edge["source"],  # vis.js uses "from" instead of "source"
                "to": edge["target"],    # vis.js uses "to" instead of "target"
                "arrows": "to",          # Show arrow pointing to target
            }
            if edge.get("label"):
                vis_edge["label"] = edge["label"]
            vis_edges.append(vis_edge)
        
        vis_js_data = {
            "nodes": vis_nodes,
            "edges": vis_edges  # vis.js expects "edges"
        }
        return json.dumps(vis_js_data)
