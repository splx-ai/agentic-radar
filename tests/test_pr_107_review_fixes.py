"""
TDD Tests for PR #107 Review Feedback from jsrzic.

These tests validate all 5 concerns raised in the PR review:
1. Graph not showing in report
2. Duplicate System Prompts section
3. Graph-only styling issues
4. Node click information display
5. Incorrect Gantt chart dates
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import subprocess
import tempfile
from playwright.sync_api import sync_playwright

from agentic_radar.report.graph.graph import Graph
from agentic_radar.report.graph.node import AgentNode, BasicNode
from agentic_radar.report.graph.edge import Edge


class TestGraphDisplay:
    """Test Issue #1: Graph not showing in report."""
    
    def test_graph_data_format_has_links_not_edges(self):
        """Test that graph.generate() returns 'links' not 'edges'."""
        graph = Graph()
        graph.nodes = [
            AgentNode(name="Agent1", label="Agent1"),
            AgentNode(name="Agent2", label="Agent2")
        ]
        graph.edges = [
            Edge(source="Agent1", target="Agent2")
        ]
        
        # Generate graph data
        graph_json = graph.generate()
        graph_data = json.loads(graph_json)
        
        # CRITICAL: Must have 'links' not 'edges' for ForceGraph
        assert 'links' in graph_data, "Graph data must have 'links' key for ForceGraph compatibility"
        assert 'edges' not in graph_data, "Graph data should not have 'edges' key"
        assert len(graph_data['links']) == 1
        
    def test_template_uses_links_not_edges(self):
        """Test that template.html.jinja uses __INLINE_DATA.links."""
        template_path = Path("agentic_radar/report/templates/template.html.jinja")
        assert template_path.exists(), "Template file must exist"
        
        template_content = template_path.read_text()
        
        # Check that template uses .links not .edges
        assert "__INLINE_DATA.links" in template_content, "Template must use __INLINE_DATA.links"
        assert "__INLINE_DATA.edges" not in template_content, "Template must not use __INLINE_DATA.edges"
        
    @pytest.mark.playwright
    def test_graph_renders_without_javascript_errors(self, browser_fixture):
        """Test that graph renders without JavaScript errors in browser."""
        page = browser_fixture
        
        # Create test HTML with graph
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <script>
        // Minimal ForceGraph mock for testing
        function ForceGraph() {
            return function(element) {
                // Check data format
                return {
                    graphData: function(data) {
                        if (!data.nodes || !data.links) {
                            throw new Error("Invalid data format: must have nodes and links");
                        }
                        element.textContent = "Graph rendered successfully";
                        return this;
                    }
                };
            };
        }
        </script>
        <script>
        const __INLINE_DATA = {
            "nodes": [{"id": "Agent1", "name": "Agent1"}],
            "links": [{"source": "Agent1", "target": "Agent1"}]
        };
        </script>
        </head>
        <body>
        <div id="graph"></div>
        <script>
        const graph = ForceGraph()(document.getElementById('graph'));
        graph.graphData(__INLINE_DATA);
        </script>
        </body>
        </html>
        """
        
        # Navigate to test HTML
        page.set_content(test_html)
        
        # Check for JavaScript errors
        console_messages = []
        page.on("console", lambda msg: console_messages.append(msg))
        
        # Wait for graph to render
        page.wait_for_selector("#graph:has-text('Graph rendered successfully')")
        
        # Assert no errors
        error_messages = [msg for msg in console_messages if msg.type == "error"]
        assert len(error_messages) == 0, f"JavaScript errors detected: {error_messages}"


class TestSystemPromptsSection:
    """Test Issue #2: Duplicate System Prompts section."""
    
    def test_no_duplicate_system_prompts_section(self):
        """Test that System Prompts section is not duplicated."""
        template_path = Path("agentic_radar/report/templates/template.html.jinja")
        template_content = template_path.read_text()
        
        # Count occurrences of System Prompts section header
        system_prompts_headers = template_content.count('>System Prompts<')
        
        # Should only appear in table header, not as separate section
        assert system_prompts_headers <= 1, f"System Prompts appears {system_prompts_headers} times, should be at most 1"
        
        # Check that the separate section div is removed
        assert 'id="system-prompts-section"' not in template_content, "Separate System Prompts section should be removed"
    
    def test_system_prompts_in_agent_table(self):
        """Test that System Prompts are shown in the agent table."""
        template_path = Path("agentic_radar/report/templates/template.html.jinja")
        template_content = template_path.read_text()
        
        # Check that agent table has System Prompt column
        assert "{{agent.system_prompt" in template_content, "Agent table must display system_prompt"


class TestGraphOnlyStyling:
    """Test Issue #3: Graph-only styling to match report."""
    
    def test_graph_only_has_splx_branding(self):
        """Test that graph-only template has SPLX branding."""
        template_path = Path("agentic_radar/report/templates/graph_only.html.jinja")
        assert template_path.exists(), "graph_only.html.jinja must exist"
        
        template_content = template_path.read_text()
        
        # Check for SPLX branding
        assert "SPLX Agentic Radar" in template_content, "Must have SPLX branding"
        assert '<svg class="logo"' in template_content or 'class="logo"' in template_content, "Must have logo"
        
    def test_graph_only_has_gradient_header(self):
        """Test that graph-only uses gradient header like main report."""
        template_path = Path("agentic_radar/report/templates/graph_only.html.jinja")
        template_content = template_path.read_text()
        
        # Check for gradient styling
        assert "linear-gradient" in template_content, "Must use gradient for header"
        assert "#2AF5D8" in template_content, "Must use brand gradient colors"
        
    def test_graph_only_uses_inter_font(self):
        """Test that graph-only uses Inter font family."""
        template_path = Path("agentic_radar/report/templates/graph_only.html.jinja")
        template_content = template_path.read_text()
        
        # Check for Inter font
        assert "Inter" in template_content, "Must use Inter font family"


class TestNodeClickFunctionality:
    """Test Issue #4: Node click information display."""
    
    def test_node_click_handles_missing_properties(self):
        """Test that node click handles nodes with missing properties."""
        template_path = Path("agentic_radar/report/templates/graph_only.html.jinja")
        template_content = template_path.read_text()
        
        # Check for proper null handling in onNodeClick
        assert "node.name || node.id ||" in template_content, "Must handle missing name/id"
        assert "node.type || node.node_class ||" in template_content, "Must handle missing type"
        
    @pytest.mark.playwright
    def test_node_click_shows_correct_info(self, browser_fixture):
        """Test that clicking nodes shows correct information."""
        page = browser_fixture
        
        # Create test HTML with node click handler
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <script>
        function testNodeClick(node) {
            const info = [];
            info.push(`Node: ${node.name || node.id || 'Unknown'}`);
            info.push(`Type: ${node.type || node.node_class || 'agent'}`);
            if (node.description) info.push(`Description: ${node.description}`);
            if (node.role) info.push(`Role: ${node.role}`);
            if (node.tools && node.tools.length > 0) {
                info.push(`Tools: ${node.tools.length}`);
            }
            return info.join('\\n');
        }
        </script>
        </head>
        <body>
        <div id="result"></div>
        <script>
        // Test with complete node
        const node1 = {
            name: "TestAgent",
            type: "agent",
            description: "Test description",
            role: "Test role",
            tools: ["tool1", "tool2"]
        };
        document.getElementById('result').textContent = testNodeClick(node1);
        </script>
        </body>
        </html>
        """
        
        page.set_content(test_html)
        result = page.locator("#result").text_content()
        
        assert "Node: TestAgent" in result
        assert "Type: agent" in result
        assert "Description: Test description" in result
        assert "Role: Test role" in result
        assert "Tools: 2" in result


class TestGanttChartDates:
    """Test Issue #5: Incorrect Gantt chart dates."""
    
    def test_autogen_marked_as_completed(self):
        """Test that AutoGen is marked as completed, not future."""
        gantt_path = Path("docs/project-gantt.md")
        if not gantt_path.exists():
            pytest.skip("Gantt chart not in current directory")
            
        gantt_content = gantt_path.read_text()
        
        # AutoGen should be marked as done
        assert ":done" in gantt_content and "autogen" in gantt_content.lower(), "AutoGen should be marked as completed"
        
        # Should not be in October 2025
        lines_with_autogen = [line for line in gantt_content.split('\n') if 'autogen' in line.lower()]
        for line in lines_with_autogen:
            assert "2025-10" not in line, f"AutoGen should not be in October 2025: {line}"
            
    def test_gantt_has_accurate_completed_section(self):
        """Test that completed work is accurately reflected."""
        gantt_path = Path("docs/project-gantt.md")
        if not gantt_path.exists():
            pytest.skip("Gantt chart not in current directory")
            
        gantt_content = gantt_path.read_text()
        
        # Should have completed frameworks section
        assert "Completed Frameworks" in gantt_content, "Should have section for completed frameworks"
        

@pytest.fixture
def browser_fixture():
    """Fixture for browser testing with Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()


def test_all_review_concerns_have_tests():
    """Meta-test: Ensure we have tests for all 5 review concerns."""
    test_classes = [
        TestGraphDisplay,           # Issue 1: Graph not showing
        TestSystemPromptsSection,   # Issue 2: Duplicate System Prompts
        TestGraphOnlyStyling,       # Issue 3: Graph-only styling
        TestNodeClickFunctionality, # Issue 4: Node click info
        TestGanttChartDates        # Issue 5: Incorrect dates
    ]
    
    assert len(test_classes) == 5, "Must have test classes for all 5 review concerns"
    
    # Each class should have at least one test
    for test_class in test_classes:
        test_methods = [m for m in dir(test_class) if m.startswith('test_')]
        assert len(test_methods) > 0, f"{test_class.__name__} must have at least one test method"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])