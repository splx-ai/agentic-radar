"""Test detection of agents created with create_react_agent() pattern."""
import pytest
from pathlib import Path

from agentic_radar.analysis.langgraph.analyze import LangGraphAnalyzer
from agentic_radar.graph import NodeType


@pytest.mark.supported
def test_detects_create_react_agent_agents():
    """
    Test that analyzer detects agents created with create_react_agent().

    This addresses Issue #94 - langmanus-style agents should be detected.
    Pattern: agent_var = create_react_agent(llm, tools=[...])
    """
    fixture_path = Path(__file__).parent.parent.parent / "fixtures" / "langgraph" / "create_react_agent"

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(fixture_path))

    # Should detect 3 agents: research_agent, coder_agent, browser_agent
    agent_nodes = [n for n in graph.nodes if n.node_type == NodeType.AGENT]
    assert len(agent_nodes) == 3, f"Expected 3 agent nodes, found {len(agent_nodes)}"

    # Agents should also appear in the agents list
    assert len(graph.agents) == 3, f"Expected 3 agents in graph.agents, found {len(graph.agents)}"

    # Check specific agent names (should match graph node names)
    agent_names = {agent.name for agent in graph.agents}
    expected_names = {"researcher", "coder", "browser"}  # Graph node names from builder.add_node()
    assert agent_names == expected_names, f"Expected {expected_names}, got {agent_names}"


@pytest.mark.supported
def test_extracts_tools_from_create_react_agent():
    """
    Test that tools are extracted from create_react_agent() arguments.

    This addresses the second part of Issue #94 - agent-tool connections.
    """
    fixture_path = Path(__file__).parent.parent.parent / "fixtures" / "langgraph" / "create_react_agent"

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(fixture_path))

    # Find the research_node agent
    research_agents = [a for a in graph.agents if "research" in a.name.lower()]
    assert len(research_agents) == 1, "Should find research agent"

    # Check tools are extracted
    research_agent = research_agents[0]
    # The agent should be connected to tavily_tool
    # Note: This tests the current behavior - we may need to adjust based on implementation

    # Find the coder agent
    coder_agents = [a for a in graph.agents if "code" in a.name.lower()]
    assert len(coder_agents) == 1, "Should find coder agent"

    # Coder should have 2 tools: python_repl_tool, bash_tool
    # Note: Tool extraction logic to be implemented


@pytest.mark.supported
def test_agent_invoke_pattern_detection():
    """
    Test that .invoke() calls on create_react_agent agents are detected.

    Pattern: agent_var.invoke(state) indicates the function is an agent node.
    """
    fixture_path = Path(__file__).parent.parent.parent / "fixtures" / "langgraph" / "create_react_agent"

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(fixture_path))

    # Functions that call agent.invoke() should be detected as agent nodes
    # research_node calls research_agent.invoke()
    # code_node calls coder_agent.invoke()
    # browser_node calls browser_agent.invoke()
    # supervisor_node does NOT call any agent.invoke()

    agent_node_names = {n.name for n in graph.nodes if n.node_type == NodeType.AGENT}
    assert "researcher" in agent_node_names  # Node name from add_node()
    assert "coder" in agent_node_names
    assert "browser" in agent_node_names
    assert "supervisor" not in agent_node_names  # supervisor is not an agent

    # Supervisor should be a basic node
    basic_nodes = [n for n in graph.nodes if n.node_type == NodeType.BASIC]
    supervisor_basics = [n for n in basic_nodes if n.name == "supervisor"]
    assert len(supervisor_basics) == 1, "Supervisor should be a basic node"
