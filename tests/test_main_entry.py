"""
Tests for the main entry point (__main__.py).

These tests ensure the module can be executed as python -m agentic_radar.
"""

import subprocess
import sys
from unittest.mock import patch


def test_main_module_execution():
    """Test that the module can be executed with python -m."""
    # Test help flag to avoid running full application
    result = subprocess.run(
        [sys.executable, "-m", "agentic_radar", "--help"],
        capture_output=True,
        text=True,
        cwd="/Users/michaeloboyle/Documents/github/agentic-radar"
    )
    
    assert result.returncode == 0
    assert "Usage:" in result.stdout


def test_main_module_version():
    """Test version flag through main module."""
    result = subprocess.run(
        [sys.executable, "-m", "agentic_radar", "--version"],
        capture_output=True,
        text=True,
        cwd="/Users/michaeloboyle/Documents/github/agentic-radar"
    )
    
    assert result.returncode == 0
    assert "SPLX Agentic Radar Version:" in result.stdout


def test_main_module_imports():
    """Test that __main__.py imports correctly."""
    # This test ensures the import in __main__.py works
    try:
        import agentic_radar.__main__
        # If we get here, imports worked
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import __main__.py: {e}")


def test_main_module_invalid_command():
    """Test main module with invalid command."""
    result = subprocess.run(
        [sys.executable, "-m", "agentic_radar", "invalid-command"],
        capture_output=True,
        text=True,
        cwd="/Users/michaeloboyle/Documents/github/agentic-radar"
    )
    
    assert result.returncode != 0