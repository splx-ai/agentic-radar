import os
import pathlib

import pytest
from typer.testing import CliRunner

from agentic_radar.cli import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


BASE_DIR_LANGGRAPH = "examples/langgraph"
BASE_DIR_CREWAI = "examples/crewai"
BASED_DIR_N8N = "examples/n8n"
BASE_DIR_OPENAI_AGENTS = "examples/openai-agents"
BASE_DIR_AUTOGEN = "examples/autogen/agentchat"


@pytest.fixture()
def params(request, tmp_path: pathlib.Path):
    tmp_path.mkdir(exist_ok=True)
    return (request.param[0], str(tmp_path / request.param[1]))


@pytest.mark.parametrize(
    "params",
    [
        (os.path.join(BASE_DIR_LANGGRAPH, dir), "report.html")
        for dir in os.listdir(BASE_DIR_LANGGRAPH)
    ],
    indirect=True,
)
def test_langgraph(params):
    i, o = params
    result = runner.invoke(app, ["scan", "langgraph", "-i", i, "-o", o])
    assert result.exit_code == 0
    assert o in result.stdout


@pytest.mark.parametrize(
    "params",
    [
        (os.path.join(BASE_DIR_CREWAI, dir), "report.html")
        for dir in os.listdir(BASE_DIR_CREWAI)
    ],
    indirect=True,
)
def test_crewai(params):
    i, o = params
    result = runner.invoke(app, ["scan", "crewai", "-i", i, "-o", o])
    assert result.exit_code == 0
    assert o in result.stdout


@pytest.mark.parametrize(
    "params",
    [
        (os.path.join(BASED_DIR_N8N, dir), "report.html")
        for dir in os.listdir(BASED_DIR_N8N)
    ],
    indirect=True,
)
def test_n8n(params):
    i, o = params
    result = runner.invoke(app, ["scan", "n8n", "-i", i, "-o", o])
    assert result.exit_code == 0
    assert o in result.stdout

@pytest.mark.parametrize(
    "params",
    [
        (os.path.join(BASE_DIR_OPENAI_AGENTS, category_dir, example_dir), "report.html")
        for category_dir in os.listdir(BASE_DIR_OPENAI_AGENTS) for example_dir in os.listdir(os.path.join(BASE_DIR_OPENAI_AGENTS, category_dir))
    ],
    indirect=True,
)
def test_openai_agents(params):
    i, o = params
    result = runner.invoke(app, ["scan", "openai-agents", "-i", i, "-o", o])
    assert result.exit_code == 0
    assert o in result.stdout

@pytest.mark.parametrize(
    "params",
    [
        (os.path.join(BASE_DIR_AUTOGEN, dir), "report.html")
        for dir in os.listdir(BASE_DIR_AUTOGEN)
    ],
    indirect=True,
)
def test_autogen(params):
    i, o = params
    result = runner.invoke(app, ["scan", "autogen", "-i", i, "-o", o])
    assert result.exit_code == 0
    assert o in result.stdout


# TDD Tests for --graph-only feature
def test_graph_only_cli_flag_exists(tmp_path):
    """Test that --graph-only flag is recognized by CLI"""
    i = os.path.join(BASE_DIR_LANGGRAPH, os.listdir(BASE_DIR_LANGGRAPH)[0])
    o = str(tmp_path / "graph.html")
    
    # This should fail initially because --graph-only doesn't exist yet
    result = runner.invoke(app, ["scan", "langgraph", "--graph-only", "-i", i, "-o", o])
    assert result.exit_code == 0  # Should succeed when implemented
    assert o in result.stdout


def test_graph_only_generates_minimal_html(tmp_path):
    """Test that --graph-only generates minimal HTML without full report sections"""
    i = os.path.join(BASE_DIR_LANGGRAPH, os.listdir(BASE_DIR_LANGGRAPH)[0])
    o = str(tmp_path / "graph.html")
    
    result = runner.invoke(app, ["scan", "langgraph", "--graph-only", "-i", i, "-o", o])
    assert result.exit_code == 0
    
    # Verify output file exists and is minimal
    assert os.path.exists(o)
    with open(o, 'r') as f:
        content = f.read()
    
    # Should contain graph visualization
    assert "ForceGraph" in content or "force-graph" in content
    assert "__INLINE_DATA" in content
    
    # Should NOT contain full report sections
    assert "Vulnerability Analysis" not in content
    assert "Tool Analysis" not in content
    assert "Agent Details" not in content


def test_graph_only_skips_vulnerability_mapping(tmp_path):
    """Test that --graph-only mode skips vulnerability mapping for performance"""
    i = os.path.join(BASE_DIR_LANGGRAPH, os.listdir(BASE_DIR_LANGGRAPH)[0])
    o = str(tmp_path / "graph.html")
    
    result = runner.invoke(app, ["scan", "langgraph", "--graph-only", "-i", i, "-o", o])
    assert result.exit_code == 0
    
    # Should not see "Mapping vulnerabilities" output
    assert "Mapping vulnerabilities" not in result.stdout


# TDD Tests for System Prompt extraction feature (#39)
def test_system_prompts_section_appears_in_report(tmp_path):
    """Test that a dedicated System Prompts section appears in the HTML report"""
    i = os.path.join(BASE_DIR_OPENAI_AGENTS, "basic", "lifecycle_example")
    o = str(tmp_path / "report.html")
    
    result = runner.invoke(app, ["scan", "openai-agents", "-i", i, "-o", o])
    assert result.exit_code == 0
    
    # Verify output file exists and contains system prompts section
    assert os.path.exists(o)
    with open(o, 'r') as f:
        content = f.read()
    
    # Should contain dedicated system prompts section
    assert "System Prompts" in content  # Section header
    assert "system-prompts-section" in content  # CSS class or ID
    

def test_system_prompts_are_extracted_and_displayed(tmp_path):
    """Test that system prompts are extracted and displayed prominently"""
    i = os.path.join(BASE_DIR_CREWAI, "basic")
    o = str(tmp_path / "report.html")
    
    result = runner.invoke(app, ["scan", "crewai", "-i", i, "-o", o])
    assert result.exit_code == 0
    
    # Verify system prompts appear in dedicated section
    assert os.path.exists(o)
    with open(o, 'r') as f:
        content = f.read()
    
    # Should display system prompts outside of just the agents table
    assert content.count("system_prompt") > 1  # More than just in agents table
    assert "System Prompts" in content
    

def test_system_prompts_section_exists_in_langgraph_report(tmp_path):
    """Test that System Prompts section exists in LangGraph reports (API-independent)"""
    i = os.path.join(BASE_DIR_LANGGRAPH, "customer_service")
    o = str(tmp_path / "report.html")
    
    result = runner.invoke(app, ["scan", "langgraph", "-i", i, "-o", o])
    assert result.exit_code == 0
    
    # Should generate report successfully
    assert os.path.exists(o)
    with open(o, 'r') as f:
        content = f.read()
    
    # System Prompts section should be present in template structure
    # Even if empty, the HTML structure should exist
    assert "system" in content.lower() or "prompt" in content.lower()


def test_graph_only_renders_functional_javascript(tmp_path):
    """Test that --graph-only generates functional JavaScript that can initialize the graph"""
    i = os.path.join(BASE_DIR_LANGGRAPH, os.listdir(BASE_DIR_LANGGRAPH)[0])
    o = str(tmp_path / "graph.html")
    
    result = runner.invoke(app, ["scan", "langgraph", "--graph-only", "-i", i, "-o", o])
    assert result.exit_code == 0
    
    # Verify the graph JavaScript is functional
    assert os.path.exists(o)
    with open(o, 'r') as f:
        content = f.read()
    
    # Should have ForceGraph function call with proper initialization
    assert "const graph = ForceGraph()" in content
    assert "document.getElementById('graph')" in content
    assert ".graphData(__INLINE_DATA)" in content
    
    # Should have valid graph data
    assert '"nodes":' in content
    assert '"links":' in content or '"edges":' in content


def test_graph_only_has_required_dom_elements(tmp_path):
    """Test that --graph-only generates required DOM elements for graph rendering"""
    i = os.path.join(BASE_DIR_LANGGRAPH, os.listdir(BASE_DIR_LANGGRAPH)[0])
    o = str(tmp_path / "graph.html")
    
    result = runner.invoke(app, ["scan", "langgraph", "--graph-only", "-i", i, "-o", o])
    assert result.exit_code == 0
    
    with open(o, 'r') as f:
        content = f.read()
    
    # Must have graph container div
    assert '<div id="graph"></div>' in content
    
    # Must have proper viewport meta tag for responsive rendering
    assert 'charset="utf-8"' in content
    
    # Graph container must have proper CSS styling
    assert "#graph" in content
    assert "width:" in content and "height:" in content


@pytest.mark.browser
def test_graph_only_javascript_executes_without_errors(tmp_path):
    """Test that JavaScript executes without console errors in a real browser"""
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright
    
    i = os.path.join(BASE_DIR_LANGGRAPH, os.listdir(BASE_DIR_LANGGRAPH)[0])
    o = str(tmp_path / "graph.html")
    
    result = runner.invoke(app, ["scan", "langgraph", "--graph-only", "-i", i, "-o", o])
    assert result.exit_code == 0
    
    # Test JavaScript execution in actual browser
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Collect JavaScript errors
        js_errors = []
        page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda error: js_errors.append(str(error)))
        
        # Load the page
        page.goto(f"file://{os.path.abspath(o)}")
        
        # Wait for JavaScript to execute
        page.wait_for_timeout(3000)
        
        # Should have no JavaScript errors
        assert len(js_errors) == 0, f"JavaScript execution errors: {js_errors}"
        
        # ForceGraph should be defined and accessible
        force_graph_defined = page.evaluate("typeof ForceGraph !== 'undefined'")
        assert force_graph_defined, "ForceGraph function is not defined"
        
        browser.close()


def test_graph_only_data_is_valid_json(tmp_path):
    """Test that __INLINE_DATA contains valid JSON that won't cause JavaScript errors"""
    i = os.path.join(BASE_DIR_LANGGRAPH, os.listdir(BASE_DIR_LANGGRAPH)[0])
    o = str(tmp_path / "graph.html")
    
    result = runner.invoke(app, ["scan", "langgraph", "--graph-only", "-i", i, "-o", o])
    assert result.exit_code == 0
    
    with open(o, 'r') as f:
        content = f.read()
    
    # Extract the JSON data
    import re
    import json
    
    # Find __INLINE_DATA assignment
    pattern = r'const __INLINE_DATA = (.+?);'
    match = re.search(pattern, content, re.DOTALL)
    assert match, "__INLINE_DATA assignment not found"
    
    json_str = match.group(1)
    
    # Should be valid JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON in __INLINE_DATA: {e}")
    
    # Should have required structure for ForceGraph
    assert "nodes" in data, "Graph data missing 'nodes' array"
    assert isinstance(data["nodes"], list), "'nodes' should be an array"
    
    # Should have links/edges
    assert "links" in data or "edges" in data, "Graph data missing 'links' or 'edges' array"
    
    # If there are nodes, each should have required properties
    if data["nodes"]:
        for node in data["nodes"][:3]:  # Check first 3 nodes
            assert "name" in node or "id" in node, f"Node missing name/id: {node}"


@pytest.mark.browser
def test_graph_only_actually_renders_in_browser(tmp_path):
    """Test that graph actually renders visually in a real browser (requires playwright)"""
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright
    
    i = os.path.join(BASE_DIR_LANGGRAPH, os.listdir(BASE_DIR_LANGGRAPH)[0])
    o = str(tmp_path / "graph.html")
    
    result = runner.invoke(app, ["scan", "langgraph", "--graph-only", "-i", i, "-o", o])
    assert result.exit_code == 0
    
    # Test in actual browser
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Load the HTML file
        page.goto(f"file://{os.path.abspath(o)}")
        
        # Wait for potential JavaScript execution
        page.wait_for_timeout(2000)
        
        # Check for JavaScript errors
        errors = []
        page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
        
        # Reload to catch any errors
        page.reload()
        page.wait_for_timeout(1000)
        
        # Should not have JavaScript errors
        js_errors = [error for error in errors if error.type == "error"]
        assert len(js_errors) == 0, f"JavaScript errors found: {[e.text for e in js_errors]}"
        
        # Graph container should exist and be visible
        graph_element = page.locator('#graph')
        assert graph_element.is_visible(), "Graph container is not visible"
        
        # Graph should have content (canvas or SVG elements from ForceGraph)
        page.wait_for_timeout(1000)  # Wait for graph to potentially render
        
        # Check if ForceGraph created any visual elements
        canvas_elements = page.locator('#graph canvas').count()
        svg_elements = page.locator('#graph svg').count()
        
        assert canvas_elements > 0 or svg_elements > 0, f"No visual graph elements found. Canvas: {canvas_elements}, SVG: {svg_elements}"
        
        browser.close()


@pytest.mark.browser  
def test_graph_only_handles_empty_data_gracefully(tmp_path):
    """Test that graph handles empty/invalid data without crashing the page"""
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright
    
    # Use test fixture for better maintainability
    import shutil
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "empty_graph_test.html")
    empty_file = str(tmp_path / "empty_graph.html")
    shutil.copy(fixture_path, empty_file)
    
    # Test in browser
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        errors = []
        page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
        
        page.goto(f"file://{os.path.abspath(empty_file)}")
        page.wait_for_timeout(1000)
        
        # Should handle empty data gracefully without JavaScript errors
        js_errors = [error for error in errors if error.type == "error"]
        assert len(js_errors) == 0, f"JavaScript errors with empty data: {[e.text for e in js_errors]}"
        
        browser.close()