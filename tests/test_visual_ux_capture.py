"""
Visual UX capture tests using Playwright screenshots.
These tests generate and save screenshots of the actual rendered graphs for visual verification.
"""

import os
import pytest
from playwright.sync_api import sync_playwright
from typer.testing import CliRunner

from agentic_radar.cli import app


@pytest.mark.browser
class TestVisualUXCapture:
    """Capture screenshots of working UX for visual regression testing."""
    
    def setup_method(self):
        """Setup CLI runner."""
        self.runner = CliRunner()
    
    def test_capture_full_report_screenshot(self, tmp_path):
        """Capture screenshot of full report UX."""
        pytest.importorskip("playwright")
        
        # Generate a real report
        input_dir = "examples/langgraph/customer_service"  # Use existing example
        output_file = str(tmp_path / "full_report.html")
        
        result = self.runner.invoke(app, [
            "scan", "langgraph", 
            "-i", input_dir, 
            "-o", output_file
        ])
        assert result.exit_code == 0
        assert os.path.exists(output_file)
        
        # Capture screenshot
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Load the report
            page.goto(f"file://{os.path.abspath(output_file)}")
            page.wait_for_timeout(3000)  # Wait for graph to render
            
            # Take full page screenshot
            screenshot_path = str(tmp_path / "full_report_screenshot.png")
            page.screenshot(path=screenshot_path, full_page=True)
            
            # Take graph section screenshot  
            graph_screenshot = str(tmp_path / "graph_section_screenshot.png")
            if page.locator('#graph').is_visible():
                page.locator('#graph').screenshot(path=graph_screenshot)
            
            browser.close()
            
        # Verify screenshots were created
        assert os.path.exists(screenshot_path)
        print(f"📸 Full report screenshot saved: {screenshot_path}")
        if os.path.exists(graph_screenshot):
            print(f"📸 Graph section screenshot saved: {graph_screenshot}")
    
    def test_capture_graph_only_screenshot(self, tmp_path):
        """Capture screenshot of graph-only UX."""
        pytest.importorskip("playwright")
        
        input_dir = "examples/langgraph/customer_service"
        output_file = str(tmp_path / "graph_only.html")
        
        result = self.runner.invoke(app, [
            "scan", "langgraph", "--graph-only",
            "-i", input_dir, 
            "-o", output_file
        ])
        assert result.exit_code == 0
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1200, "height": 800})
            
            page.goto(f"file://{os.path.abspath(output_file)}")
            page.wait_for_timeout(2000)
            
            screenshot_path = str(tmp_path / "graph_only_screenshot.png")
            page.screenshot(path=screenshot_path, full_page=True)
            
            browser.close()
        
        assert os.path.exists(screenshot_path)
        print(f"📸 Graph-only screenshot saved: {screenshot_path}")
    
    def test_capture_vis_js_vs_force_graph_comparison(self, tmp_path):
        """Capture side-by-side comparison of vis.js vs ForceGraph.js."""
        pytest.importorskip("playwright")
        
        input_dir = "examples/langgraph/customer_service"
        
        # Generate both formats
        force_graph_file = str(tmp_path / "force_graph.html")
        vis_js_file = str(tmp_path / "vis_js.html")
        
        # ForceGraph version (default)
        result1 = self.runner.invoke(app, [
            "scan", "langgraph", "--graph-only", "--visualization", "force-graph",
            "-i", input_dir, "-o", force_graph_file
        ])
        assert result1.exit_code == 0
        
        # vis.js version  
        result2 = self.runner.invoke(app, [
            "scan", "langgraph", "--graph-only", "--visualization", "vis-js",
            "-i", input_dir, "-o", vis_js_file
        ])
        assert result2.exit_code == 0
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            # Capture ForceGraph version
            page1 = browser.new_page()
            page1.set_viewport_size({"width": 1200, "height": 800})
            page1.goto(f"file://{os.path.abspath(force_graph_file)}")
            page1.wait_for_timeout(2000)
            
            force_graph_screenshot = str(tmp_path / "force_graph_screenshot.png")
            page1.screenshot(path=force_graph_screenshot, full_page=True)
            
            # Capture vis.js version
            page2 = browser.new_page()
            page2.set_viewport_size({"width": 1200, "height": 800})
            page2.goto(f"file://{os.path.abspath(vis_js_file)}")
            page2.wait_for_timeout(2000)
            
            vis_js_screenshot = str(tmp_path / "vis_js_screenshot.png")
            page2.screenshot(path=vis_js_screenshot, full_page=True)
            
            browser.close()
        
        assert os.path.exists(force_graph_screenshot)
        assert os.path.exists(vis_js_screenshot)
        print(f"📸 ForceGraph screenshot: {force_graph_screenshot}")
        print(f"📸 vis.js screenshot: {vis_js_screenshot}")
    
    def test_capture_interactive_elements(self, tmp_path):
        """Capture screenshots of interactive elements (hover, click states)."""
        pytest.importorskip("playwright")
        
        input_dir = "examples/langgraph/customer_service"
        output_file = str(tmp_path / "interactive.html")
        
        result = self.runner.invoke(app, [
            "scan", "langgraph", "--graph-only",
            "-i", input_dir, "-o", output_file
        ])
        assert result.exit_code == 0
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1200, "height": 800})
            
            page.goto(f"file://{os.path.abspath(output_file)}")
            page.wait_for_timeout(3000)
            
            # Capture default state
            default_screenshot = str(tmp_path / "default_state.png")
            page.screenshot(path=default_screenshot, full_page=True)
            
            # Try to interact with graph (hover over controls, etc.)
            controls = page.locator('.controls')
            if controls.is_visible():
                controls.hover()
                page.wait_for_timeout(500)
                
                hover_screenshot = str(tmp_path / "controls_hover.png")
                page.screenshot(path=hover_screenshot, full_page=True)
                
                print(f"📸 Hover state screenshot: {hover_screenshot}")
            
            browser.close()
            
        assert os.path.exists(default_screenshot)
        print(f"📸 Default state screenshot: {default_screenshot}")
    
    def test_responsive_screenshots(self, tmp_path):
        """Capture screenshots at different viewport sizes."""
        pytest.importorskip("playwright")
        
        input_dir = "examples/langgraph/customer_service"
        output_file = str(tmp_path / "responsive.html")
        
        result = self.runner.invoke(app, [
            "scan", "langgraph", "--graph-only",
            "-i", input_dir, "-o", output_file
        ])
        assert result.exit_code == 0
        
        viewports = [
            {"name": "desktop", "width": 1920, "height": 1080},
            {"name": "tablet", "width": 1024, "height": 768},
            {"name": "mobile", "width": 375, "height": 667},
        ]
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            for viewport in viewports:
                page = browser.new_page()
                page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
                
                page.goto(f"file://{os.path.abspath(output_file)}")
                page.wait_for_timeout(2000)
                
                screenshot_path = str(tmp_path / f"{viewport['name']}_screenshot.png")
                page.screenshot(path=screenshot_path, full_page=True)
                
                print(f"📸 {viewport['name']} ({viewport['width']}x{viewport['height']}): {screenshot_path}")
                assert os.path.exists(screenshot_path)
            
            browser.close()


@pytest.mark.browser  
def test_visual_regression_baseline(tmp_path):
    """Create visual baseline for regression testing."""
    pytest.importorskip("playwright")
    
    # This test would compare current screenshots against saved baselines
    # For now, it demonstrates the pattern
    
    runner = CliRunner()
    input_dir = "examples/langgraph/basic"
    output_file = str(tmp_path / "baseline.html")
    
    result = runner.invoke(app, [
        "scan", "langgraph", "--graph-only",
        "-i", input_dir, "-o", output_file
    ])
    assert result.exit_code == 0
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1200, "height": 800})
        
        page.goto(f"file://{os.path.abspath(output_file)}")
        page.wait_for_timeout(2000)
        
        # In a real scenario, you'd compare against a saved baseline
        current_screenshot = str(tmp_path / "current_baseline.png")
        page.screenshot(path=current_screenshot, full_page=True)
        
        browser.close()
    
    assert os.path.exists(current_screenshot)
    print(f"📸 Baseline screenshot created: {current_screenshot}")
    
    # Future: Add image comparison logic here
    # Example: assert images_are_similar(current_screenshot, "tests/baselines/expected_baseline.png")