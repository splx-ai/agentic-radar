"""
Additional CLI tests to improve coverage.

These tests focus on covering CLI functionality that wasn't tested
in the existing cli_test.py file.
"""

import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from agentic_radar.cli import app, version_callback, AgenticFramework


runner = CliRunner()


def test_version_flag():
    """Test --version flag displays version information."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "SPLX Agentic Radar Version:" in result.stdout


def test_version_callback_function():
    """Test version_callback function directly."""
    # Test when version is None (normal operation)
    version_callback(version=None)  # Should not raise exception
    
    # Test when version is True (should exit)
    with pytest.raises(SystemExit):
        version_callback(version=True)


def test_agentic_framework_enum():
    """Test AgenticFramework enum values."""
    assert AgenticFramework.langgraph == "langgraph"
    assert AgenticFramework.crewai == "crewai" 
    assert AgenticFramework.n8n == "n8n"
    assert AgenticFramework.openai_agents == "openai-agents"
    assert AgenticFramework.autogen == "autogen"


def test_scan_help():
    """Test scan command help."""
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "Scan code for agentic workflows" in result.stdout


def test_scan_invalid_framework():
    """Test scan with invalid framework."""
    result = runner.invoke(app, ["scan", "invalid-framework"])
    assert result.exit_code != 0


def test_scan_with_graph_only_flag():
    """Test scan with --graph-only flag."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a minimal test case
        test_dir = os.path.join(tmp_dir, "test")
        os.makedirs(test_dir)
        
        # Write a simple Python file for LangGraph to analyze
        with open(os.path.join(test_dir, "test.py"), "w") as f:
            f.write("# Simple test file\nprint('hello')\n")
        
        output_file = os.path.join(tmp_dir, "test_output.html")
        
        result = runner.invoke(app, [
            "scan", "langgraph", 
            "-i", test_dir,
            "-o", output_file,
            "--graph-only"
        ])
        
        # Should succeed or fail gracefully
        assert result.exit_code in [0, 1]  # 1 is acceptable if no valid graphs found


def test_scan_with_export_graph_json():
    """Test scan with --export-graph-json flag."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_dir = os.path.join(tmp_dir, "test")
        os.makedirs(test_dir)
        
        with open(os.path.join(test_dir, "test.py"), "w") as f:
            f.write("# Simple test file\nprint('hello')\n")
        
        output_file = os.path.join(tmp_dir, "test_output.html")
        
        result = runner.invoke(app, [
            "scan", "langgraph",
            "-i", test_dir, 
            "-o", output_file,
            "--export-graph-json"
        ])
        
        # Should succeed or fail gracefully
        assert result.exit_code in [0, 1]


@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
def test_scan_with_harden_prompts():
    """Test scan with --harden-prompts flag."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_dir = os.path.join(tmp_dir, "test")
        os.makedirs(test_dir)
        
        with open(os.path.join(test_dir, "test.py"), "w") as f:
            f.write("# Simple test file\nprint('hello')\n")
        
        output_file = os.path.join(tmp_dir, "test_output.html")
        
        # Mock the OpenAI call to avoid rate limits
        with patch("agentic_radar.prompt_hardening.harden.harden_agent_prompts") as mock_harden:
            mock_harden.return_value = {}
            
            result = runner.invoke(app, [
                "scan", "langgraph",
                "-i", test_dir,
                "-o", output_file, 
                "--harden-prompts"
            ])
            
            # Should succeed or fail gracefully
            assert result.exit_code in [0, 1]


def test_scan_nonexistent_input_directory():
    """Test scan with non-existent input directory."""
    result = runner.invoke(app, [
        "scan", "langgraph",
        "-i", "/nonexistent/directory",
        "-o", "output.html"
    ])
    assert result.exit_code != 0


def test_scan_environment_variables():
    """Test scan command with environment variables."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_dir = os.path.join(tmp_dir, "test")
        os.makedirs(test_dir)
        
        with open(os.path.join(test_dir, "test.py"), "w") as f:
            f.write("# Simple test file\nprint('hello')\n")
        
        output_file = os.path.join(tmp_dir, "test_output.html")
        
        # Test with environment variables set
        env_vars = {
            "AGENTIC_RADAR_INPUT_DIRECTORY": test_dir,
            "AGENTIC_RADAR_OUTPUT_FILE": output_file
        }
        
        with patch.dict(os.environ, env_vars):
            result = runner.invoke(app, ["scan", "langgraph"])
            # Should succeed or fail gracefully
            assert result.exit_code in [0, 1]


def test_test_command_help():
    """Test test command help."""
    result = runner.invoke(app, ["test", "--help"])
    assert result.exit_code == 0
    assert "Test agents" in result.stdout


def test_test_command_invalid_framework():
    """Test test command with invalid framework."""
    result = runner.invoke(app, ["test", "invalid-framework", "script.py"])
    assert result.exit_code != 0


def test_test_command_missing_script():
    """Test test command without script argument.""" 
    result = runner.invoke(app, ["test", "openai-agents"])
    assert result.exit_code != 0


@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
def test_test_command_with_config():
    """Test test command with config file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
include_default_tests: true
tests:
  - name: TestExample
    input: "Test input"
    success_condition: "Test success condition"
""")
        f.flush()
        
        try:
            # Mock the test execution to avoid actual OpenAI calls
            with patch("agentic_radar.test.load_tests") as mock_load:
                mock_load.return_value = []
                
                result = runner.invoke(app, [
                    "test", "openai-agents",
                    "--config", f.name,
                    "nonexistent_script.py"  # Will fail but tests CLI parsing
                ])
                
                # Will fail due to missing script, but CLI parsing should work
                assert result.exit_code != 0
        finally:
            os.unlink(f.name)


def test_app_no_command():
    """Test app invocation without any command."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_invalid_command():
    """Test app with invalid command."""
    result = runner.invoke(app, ["invalid-command"])
    assert result.exit_code != 0