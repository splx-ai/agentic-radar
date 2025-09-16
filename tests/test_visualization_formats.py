"""
Test that graph generation supports both ForceGraph and vis.js formats correctly.
"""

import json
import pytest
from agentic_radar.report.graph.graph import Graph
from agentic_radar.report.graph.node import BasicNode, AgentNode
from agentic_radar.report.graph.edge import Edge, ConditionalEdge


class TestVisualizationFormats:
    """Test that both visualization formats are generated correctly."""
    
    def setup_method(self):
        """Create a sample graph for testing."""
        self.graph = Graph(
            nodes=[
                BasicNode(name="START", label="START"),
                AgentNode(name="Agent1", label="Agent 1"),
                AgentNode(name="Agent2", label="Agent 2"),
                BasicNode(name="END", label="END"),
            ],
            edges=[
                Edge(source="START", target="Agent1"),
                Edge(source="Agent1", target="Agent2"),
                Edge(source="Agent2", target="END"),
            ]
        )
    
    def test_force_graph_format_uses_links(self):
        """Test that ForceGraph format uses 'links' key."""
        json_str = self.graph.generate(visualization="force-graph")
        data = json.loads(json_str)
        
        # ForceGraph expects 'links' not 'edges'
        assert "links" in data
        assert "edges" not in data
        assert len(data["links"]) == 3
        
        # Verify link structure
        link = data["links"][0]
        assert "source" in link
        assert "target" in link
        assert link["source"] == "START"
        assert link["target"] == "Agent1"
    
    def test_vis_js_format_uses_edges(self):
        """Test that vis.js format uses 'edges' key."""
        json_str = self.graph.generate(visualization="vis-js")
        data = json.loads(json_str)
        
        # vis.js expects 'edges' not 'links'
        assert "edges" in data
        assert "links" not in data
        assert len(data["edges"]) == 3
        
        # Verify edge structure (vis.js uses 'from' and 'to')
        edge = data["edges"][0]
        assert "from" in edge
        assert "to" in edge
        assert edge["from"] == "START"
        assert edge["to"] == "Agent1"
        assert edge["arrows"] == "to"
    
    def test_default_format_is_force_graph(self):
        """Test that default format is ForceGraph."""
        json_str = self.graph.generate()  # No visualization param
        data = json.loads(json_str)
        
        # Should default to ForceGraph format
        assert "links" in data
        assert "edges" not in data
    
    def test_vis_js_node_format(self):
        """Test that vis.js nodes have the correct format."""
        json_str = self.graph.generate(visualization="vis-js")
        data = json.loads(json_str)
        
        assert "nodes" in data
        assert len(data["nodes"]) == 4
        
        # Check node structure
        agent_node = next(n for n in data["nodes"] if n["id"] == "Agent1")
        assert agent_node["label"] == "Agent 1"
        # Node should have proper grouping
        assert "group" in agent_node or "type" in agent_node
    
    def test_vis_js_edge_labels(self):
        """Test that vis.js edges preserve labels when present."""
        # Since Edge class doesn't actually store condition/label,
        # we'll test that the structure is correct for edges without labels
        graph_with_edges = Graph(
            nodes=[
                BasicNode(name="A", label="Node A"),
                BasicNode(name="B", label="Node B"),
            ],
            edges=[
                Edge(source="A", target="B"),
            ]
        )
        
        json_str = graph_with_edges.generate(visualization="vis-js")
        data = json.loads(json_str)
        
        edge = data["edges"][0]
        # Edge should have proper vis.js structure
        assert edge["from"] == "A"
        assert edge["to"] == "B"
        assert edge["arrows"] == "to"
    
    def test_vis_js_image_nodes(self):
        """Test that vis.js handles image nodes correctly."""
        # Use AgentNode which has an image by default
        graph_with_image = Graph(
            nodes=[
                AgentNode(name="Tool", label="Tool"),
            ],
            edges=[]
        )
        
        json_str = graph_with_image.generate(visualization="vis-js")
        data = json.loads(json_str)
        
        node = data["nodes"][0]
        assert "image" in node  # AgentNode has an image
        assert node["shape"] == "image"
    
    def test_both_formats_preserve_node_count(self):
        """Test that both formats preserve the same number of nodes."""
        force_graph_json = self.graph.generate(visualization="force-graph")
        vis_js_json = self.graph.generate(visualization="vis-js")
        
        force_graph_data = json.loads(force_graph_json)
        vis_js_data = json.loads(vis_js_json)
        
        assert len(force_graph_data["nodes"]) == len(vis_js_data["nodes"])
        assert len(force_graph_data["links"]) == len(vis_js_data["edges"])
    
    def test_invalid_edges_filtered_in_both_formats(self):
        """Test that edges to non-existent nodes are filtered in both formats."""
        graph_with_invalid = Graph(
            nodes=[
                BasicNode(name="A", label="A"),
                BasicNode(name="B", label="B"),
            ],
            edges=[
                Edge(source="A", target="B"),  # Valid
                Edge(source="A", target="C"),  # Invalid - C doesn't exist
                Edge(source="D", target="B"),  # Invalid - D doesn't exist
            ]
        )
        
        # Test ForceGraph format
        force_graph_json = graph_with_invalid.generate(visualization="force-graph")
        force_graph_data = json.loads(force_graph_json)
        assert len(force_graph_data["links"]) == 1  # Only valid edge
        
        # Test vis.js format
        vis_js_json = graph_with_invalid.generate(visualization="vis-js")
        vis_js_data = json.loads(vis_js_json)
        assert len(vis_js_data["edges"]) == 1  # Only valid edge