#!/usr/bin/env python3
"""
Generate screenshots for PR documentation.
This script creates visual documentation to accompany pull requests.
"""

import os
import tempfile
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

def run_screenshot_tests() -> Dict[str, List[str]]:
    """Run screenshot tests and return paths to generated images."""
    
    # Create output directory
    output_dir = Path("pr-screenshots")
    output_dir.mkdir(exist_ok=True)
    
    screenshot_map = {}
    
    # Test configurations
    test_configs = [
        {
            "name": "Full Report",
            "test": "tests/test_visual_ux_capture.py::TestVisualUXCapture::test_capture_full_report_screenshot",
            "description": "Complete HTML report with all sections"
        },
        {
            "name": "Graph Only",
            "test": "tests/test_visual_ux_capture.py::TestVisualUXCapture::test_capture_graph_only_screenshot", 
            "description": "Minimal graph visualization (--graph-only flag)"
        },
        {
            "name": "Visualization Comparison",
            "test": "tests/test_visual_ux_capture.py::TestVisualUXCapture::test_capture_vis_js_vs_force_graph_comparison",
            "description": "Side-by-side comparison of ForceGraph.js vs vis.js"
        },
        {
            "name": "Responsive Views",
            "test": "tests/test_visual_ux_capture.py::TestVisualUXCapture::test_responsive_screenshots",
            "description": "Screenshots at different viewport sizes"
        }
    ]
    
    for config in test_configs:
        print(f"🔄 Generating {config['name']} screenshots...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Run the test with temporary directory
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    config["test"],
                    f"--basetemp={temp_dir}",
                    "-v", "-s", "--tb=short"
                ], capture_output=True, text=True, timeout=60)
                
                # Find generated screenshots in temp directory
                temp_screenshots = list(Path(temp_dir).rglob("*.png"))
                
                copied_files = []
                for screenshot in temp_screenshots:
                    # Copy to PR screenshots directory with descriptive name
                    new_name = f"{config['name'].lower().replace(' ', '_')}_{screenshot.name}"
                    dest_path = output_dir / new_name
                    
                    import shutil
                    shutil.copy2(screenshot, dest_path)
                    copied_files.append(str(dest_path))
                    print(f"📸 Saved: {dest_path}")
                
                screenshot_map[config['name']] = {
                    'files': copied_files,
                    'description': config['description'],
                    'success': result.returncode == 0
                }
                
                if result.returncode != 0:
                    print(f"⚠️  Test failed for {config['name']}: {result.stderr}")
                
            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout generating {config['name']} screenshots")
                screenshot_map[config['name']] = {
                    'files': [],
                    'description': config['description'],
                    'success': False,
                    'error': 'Timeout'
                }
            except Exception as e:
                print(f"❌ Error generating {config['name']} screenshots: {e}")
                screenshot_map[config['name']] = {
                    'files': [],
                    'description': config['description'], 
                    'success': False,
                    'error': str(e)
                }
    
    return screenshot_map

def generate_pr_comment(screenshot_map: Dict[str, Any]) -> str:
    """Generate markdown comment for PR with screenshot information."""
    
    comment = "## 📸 Visual Changes Preview\n\n"
    comment += "Screenshots have been generated to show the visual impact of these changes.\n\n"
    
    successful_screenshots = sum(1 for data in screenshot_map.values() if data['success'] and data['files'])
    total_files = sum(len(data['files']) for data in screenshot_map.values() if data['success'])
    
    if total_files == 0:
        comment += "⚠️ No screenshots were generated. This may indicate:\n"
        comment += "- The changes don't affect visual output\n"
        comment += "- Test environment issues\n"
        comment += "- Missing example data\n\n"
        return comment
    
    comment += f"**Generated {total_files} screenshots across {successful_screenshots} test categories:**\n\n"
    
    for category, data in screenshot_map.items():
        if data['success'] and data['files']:
            comment += f"### {category}\n"
            comment += f"*{data['description']}*\n\n"
            
            for file_path in data['files']:
                file_name = Path(file_path).name
                comment += f"- `{file_name}`\n"
            comment += "\n"
        elif not data['success']:
            comment += f"### ⚠️ {category} (Failed)\n"
            comment += f"*{data['description']}*\n"
            if 'error' in data:
                comment += f"Error: {data['error']}\n"
            comment += "\n"
    
    comment += "**How to View Screenshots:**\n"
    comment += "1. Go to the [Actions tab](../../actions) for this PR\n"
    comment += "2. Click on the latest 'Generate PR Screenshots' workflow run\n" 
    comment += "3. Download the 'pr-screenshots' artifact\n"
    comment += "4. Unzip to view the PNG files\n\n"
    
    comment += "> 🤖 Screenshots automatically generated to help review visual changes.\n"
    comment += "> These show the actual rendered UI in a real browser environment."
    
    return comment

def main():
    """Main function to generate screenshots and PR comment."""
    print("🚀 Generating PR screenshots...")
    
    # Check if we're in the right directory
    if not Path("agentic_radar").exists():
        print("❌ Must be run from the repository root directory")
        sys.exit(1)
    
    # Generate screenshots
    screenshot_map = run_screenshot_tests()
    
    # Generate PR comment
    pr_comment = generate_pr_comment(screenshot_map)
    
    # Save PR comment to file
    comment_file = Path("pr-screenshots") / "PR_COMMENT.md"
    comment_file.write_text(pr_comment)
    
    print(f"\n✅ Screenshot generation complete!")
    print(f"📁 Screenshots saved to: pr-screenshots/")
    print(f"📝 PR comment saved to: {comment_file}")
    print(f"\n📋 Copy this to your PR description:\n")
    print("-" * 50)
    print(pr_comment)
    print("-" * 50)

if __name__ == "__main__":
    main()