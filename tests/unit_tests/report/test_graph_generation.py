"""Tests for graph generation and JavaScript runtime compatibility (Issue #35)"""

import json

import pytest

from agentic_radar.report.graph.edge import Edge
from agentic_radar.report.graph.graph import Graph
from agentic_radar.report.graph.node import AgentNode, BasicNode, ToolNode


class TestGraphGeneration:
    """Test graph data generation for ForceGraph.js compatibility."""

    def test_graph_generate_produces_links_not_edges(self):
        """Test that Graph.generate() outputs 'links' key, not 'edges' (Issue #35 fix)."""
        # Create test graph with nodes and edges
        graph = Graph(
            nodes=[
                BasicNode(name="START", label="Start"),
                AgentNode(name="Agent1", label="Agent 1"),
                BasicNode(name="END", label="End")
            ],
            edges=[
                Edge(source="START", target="Agent1"),
                Edge(source="Agent1", target="END")
            ]
        )

        # Generate JSON output
        graph_json = graph.generate()
        data = json.loads(graph_json)

        # Assert ForceGraph.js compatible format
        assert "links" in data, "Graph should contain 'links' key for ForceGraph.js"
        assert "edges" not in data, "Graph should not contain 'edges' key (causes JS runtime error)"
        assert len(data["links"]) == 2, "Should have 2 links"
        assert data["links"][0]["source"] == "START"
        assert data["links"][0]["target"] == "Agent1"
        assert data["links"][1]["source"] == "Agent1"
        assert data["links"][1]["target"] == "END"

    def test_graph_generate_preserves_nodes(self):
        """Test that nodes are preserved correctly in output."""
        graph = Graph(
            nodes=[
                AgentNode(name="TestAgent", label="Test Agent"),
                ToolNode(name="TestTool", label="Test Tool")
            ],
            edges=[]
        )

        graph_json = graph.generate()
        data = json.loads(graph_json)

        assert "nodes" in data
        assert len(data["nodes"]) == 2
        assert data["nodes"][0]["name"] == "TestAgent"
        assert data["nodes"][0]["label"] == "Test Agent"
        assert "image" in data["nodes"][0]  # Should have SVG image data

    def test_empty_graph_generates_valid_json(self):
        """Test that empty graphs generate valid JSON without errors."""
        graph = Graph()

        graph_json = graph.generate()
        data = json.loads(graph_json)

        assert "nodes" in data
        assert "links" in data
        assert data["nodes"] == []
        assert data["links"] == []

    def test_graph_with_only_nodes_generates_correctly(self):
        """Test graphs with nodes but no edges."""
        graph = Graph(
            nodes=[AgentNode(name="Isolated", label="Isolated Agent")],
            edges=[]
        )

        graph_json = graph.generate()
        data = json.loads(graph_json)

        assert len(data["nodes"]) == 1
        assert len(data["links"]) == 0
        assert "edges" not in data


class TestJavaScriptRuntimeCompatibility:
    """Test that generated data is compatible with JavaScript runtime expectations."""

    def test_javascript_runtime_data_format(self):
        """Test that data format matches what ForceGraph.js expects in template."""
        graph = Graph(
            nodes=[
                BasicNode(name="START", label="Start"),
                AgentNode(name="Agent", label="Agent")
            ],
            edges=[
                Edge(source="START", target="Agent")
            ]
        )

        graph_json = graph.generate()

        # Simulate what happens in template.html.jinja
        inline_data = json.loads(graph_json)

        # This should NOT raise a KeyError (the Issue #35 bug)
        try:
            links = inline_data["links"]  # This is what template.html.jinja expects
            assert len(links) == 1
        except KeyError as e:
            pytest.fail(f"JavaScript runtime error reproduced: {e}")

        # This WOULD raise KeyError in the old broken version
        with pytest.raises(KeyError):
            _ = inline_data["edges"]  # This key should not exist

    def test_force_graph_data_structure(self):
        """Test that data structure matches ForceGraph.js requirements."""
        graph = Graph(
            nodes=[
                AgentNode(name="N1", label="Node 1"),
                ToolNode(name="N2", label="Node 2")
            ],
            edges=[
                Edge(source="N1", target="N2")
            ]
        )

        data = json.loads(graph.generate())

        # ForceGraph.js expects this exact structure
        assert set(data.keys()) == {"nodes", "links"}

        # Links should have source/target (not from/to like vis.js)
        link = data["links"][0]
        assert "source" in link
        assert "target" in link
        assert link["source"] == "N1"
        assert link["target"] == "N2"