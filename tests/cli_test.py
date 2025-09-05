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
    assert "force-graph.js" in content
    assert "__INLINE_DATA" in content
    
    # Should NOT contain full report sections
    assert "Vulnerability Analysis" not in content
    assert "Tool Analysis" not in content
    assert "Agent Details" not in content


def test_graph_only_skips_vulnerability_mapping(tmp_path, capsys):
    """Test that --graph-only mode skips vulnerability mapping for performance"""
    i = os.path.join(BASE_DIR_LANGGRAPH, os.listdir(BASE_DIR_LANGGRAPH)[0])
    o = str(tmp_path / "graph.html")
    
    result = runner.invoke(app, ["scan", "langgraph", "--graph-only", "-i", i, "-o", o])
    assert result.exit_code == 0
    
    # Should not see "Mapping vulnerabilities" output
    assert "Mapping vulnerabilities" not in result.stdout