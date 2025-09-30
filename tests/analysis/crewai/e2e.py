import json
from textwrap import dedent
from pathlib import Path

import pytest

from agentic_radar.analysis.crewai.analyze import CrewAIAnalyzer
from agentic_radar.graph import NodeType


# =====================
# Fixtures
# =====================


@pytest.fixture(scope="module")
def analyzer() -> CrewAIAnalyzer:
    """Provide a single analyzer instance for all tests in this module."""
    return CrewAIAnalyzer()


@pytest.fixture
def code_workspace(tmp_path: Path):
    """Utility fixture that writes provided code files into an isolated temp dir.

    Returns a function write(files: dict[str,str]) -> Path which, when called,
    writes the mapping of relative file path -> file contents into the temp dir
    and returns the root directory path for analysis.
    """

    def _writer(files: dict[str, str]) -> Path:
        for rel, content in files.items():
            file_path = tmp_path / rel
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(dedent(content))
        return tmp_path

    return _writer


def _run(analyzer: CrewAIAnalyzer, root: Path):
    """Execute analyzer and return graph plus helper lookups."""
    graph = analyzer.analyze(str(root))
    # Build lookups for convenience
    nodes_by_name = {n.name: n for n in graph.nodes}
    outgoing = {}
    for e in graph.edges:
        outgoing.setdefault(e.start, set()).add(e.end)
    return graph, nodes_by_name, outgoing


def _assert_agent_to_mcp(agent: str, mcp: str, outgoing: dict):
    assert agent in outgoing, f"Agent {agent} missing from outgoing edges"
    assert mcp in outgoing[agent], f"Expected edge {agent}->{mcp} for MCP connection"


# =====================
# Test Scenarios
# =====================


def test_mcp_with_adapter_all_tools(analyzer: CrewAIAnalyzer, code_workspace):
    """Pattern: with MCPServerAdapter(server_params) as mcp_tools then Agent(..., tools=mcp_tools)."""
    server_code = """
    from crewai_tools import MCPServerAdapter
    from mcp import StdioServerParameters
    from crewai import Agent, Task, Crew
    import os

    server_params = StdioServerParameters(command="python3", args=["srv.py"], env={"UV_PYTHON": "3.12", **os.environ})

    with MCPServerAdapter(server_params, connect_timeout=1) as mcp_tools:
        my_agent = Agent(role="R", goal="G", backstory="B", tools=mcp_tools)
        t = Task(description="d", expected_output="o", agent=my_agent)
        crew = Crew(agents=[my_agent], tasks=[t])
    """
    root = code_workspace({"proj/code.py": server_code})

    graph, nodes, outgoing = _run(analyzer, root)

    # Expect agent node and one MCP node with same variable name 'server_params'
    assert "my_agent" in nodes
    # MCP node name inferred from variable holding params: server_params
    assert "server_params" in nodes, f"MCP server node not found. Nodes: {list(nodes)}"
    assert nodes["server_params"].node_type == NodeType.MCP_SERVER
    _assert_agent_to_mcp("my_agent", "server_params", outgoing)


def test_mcp_with_adapter_subset_tool(analyzer: CrewAIAnalyzer, code_workspace):
    """Pattern: tools=[mcp_tools["name"]] subscript indexing should still attach MCP server."""
    code = """
    from crewai_tools import MCPServerAdapter
    from crewai import Agent, Task, Crew
    server_params = {"url": "http://localhost:8001/mcp", "transport": "streamable-http"}
    with MCPServerAdapter(server_params) as mcp_tools:
        subset_agent = Agent(role="R2", goal="G2", backstory="B2", tools=[mcp_tools["tool_name"]])
        t = Task(description="d", expected_output="o", agent=subset_agent)
        crew = Crew(agents=[subset_agent], tasks=[t])
    """
    root = code_workspace({"proj/code.py": code})
    graph, nodes, outgoing = _run(analyzer, root)

    assert "subset_agent" in nodes
    assert "server_params" in nodes
    assert nodes["server_params"].node_type == NodeType.MCP_SERVER
    _assert_agent_to_mcp("subset_agent", "server_params", outgoing)


def test_mcp_list_in_crewbase(analyzer: CrewAIAnalyzer, code_workspace):
    """Pattern: CrewBase class with mcp_server_params list including dict + StdioServerParameters call."""
    code = """
    from crewai import Agent, Task, Crew, Process
    from crewai.project import CrewBase, agent, task, crew
    from mcp import StdioServerParameters

    @CrewBase
    class DemoCrew:
        mcp_server_params = [
            {"url": "http://localhost:8001/mcp", "transport": "streamable-http"},
            StdioServerParameters(command="python3", args=["x.py"], env={})
        ]

        @agent
        def a1(self) -> Agent:
            return Agent(role="R3", goal="G3", backstory="B3", tools=self.get_mcp_tools())

        @task
        def t1(self) -> Task:
            return Task(description="d", expected_output="o", agent=self.a1())

        @crew
        def crew(self) -> Crew:
            return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential)
    """
    root = code_workspace({"proj/crew.py": code})
    graph, nodes, outgoing = _run(analyzer, root)

    # The visitor names them mcp_server_params_1, mcp_server_params_2
    mcp1 = "mcp_server_params_1"
    mcp2 = "mcp_server_params_2"
    assert mcp1 in nodes and mcp2 in nodes
    assert nodes[mcp1].node_type == nodes[mcp2].node_type == NodeType.MCP_SERVER

    # Agent method name becomes node name 'a1'
    assert "a1" in nodes
    _assert_agent_to_mcp("a1", mcp1, outgoing)
    _assert_agent_to_mcp("a1", mcp2, outgoing)

    # Ensure params encoded in description as JSON for at least first MCP
    desc = nodes[mcp1].description
    assert desc is not None
    loaded = json.loads(desc)
    assert loaded.get("url") == "http://localhost:8001/mcp"


# =====================
# Minimal smoke to ensure edges include START/END when applicable (Crew processes)
# =====================


def test_no_duplicate_mcp_nodes(analyzer: CrewAIAnalyzer, code_workspace):
    """Multiple agents referencing same server_params should yield single MCP node."""
    code = """
    from crewai import Agent, Task, Crew
    from crewai_tools import MCPServerAdapter
    server_params = {"url": "http://localhost:8001/mcp", "transport": "streamable-http"}
    with MCPServerAdapter(server_params) as mcp_tools:
        a1 = Agent(role="r", goal="g", backstory="b", tools=mcp_tools)
        a2 = Agent(role="r2", goal="g2", backstory="b2", tools=[mcp_tools["tool_name"]])
        t1 = Task(description="d1", expected_output="o1", agent=a1)
        t2 = Task(description="d2", expected_output="o2", agent=a2)
        crew = Crew(agents=[a1, a2], tasks=[t1, t2])
    """
    root = code_workspace({"proj/code.py": code})
    graph, nodes, outgoing = _run(analyzer, root)
    assert "server_params" in nodes
    assert nodes["server_params"].node_type == NodeType.MCP_SERVER
    _assert_agent_to_mcp("a1", "server_params", outgoing)
    _assert_agent_to_mcp("a2", "server_params", outgoing)

    # Ensure only one MCP node with that name
    mcp_nodes = [n for n in graph.nodes if n.node_type == NodeType.MCP_SERVER and n.name == "server_params"]
    assert len(mcp_nodes) == 1
