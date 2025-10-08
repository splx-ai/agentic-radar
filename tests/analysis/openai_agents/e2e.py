from pathlib import Path
from textwrap import dedent
import json

import pytest

from agentic_radar.analysis.openai_agents.analyze import OpenAIAgentsAnalyzer
from agentic_radar.graph import NodeType


# ================= Fixtures =================

@pytest.fixture(scope="module")
def analyzer() -> OpenAIAgentsAnalyzer:
    return OpenAIAgentsAnalyzer()


@pytest.fixture
def code_workspace(tmp_path: Path):
    def _writer(files: dict[str, str]) -> Path:
        for rel, content in files.items():
            p = tmp_path / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(dedent(content))
        return tmp_path
    return _writer


def _run(analyzer: OpenAIAgentsAnalyzer, root: Path):
    graph = analyzer.analyze(str(root))
    nodes = {n.name: n for n in graph.nodes}
    outgoing = {}
    for e in graph.edges:
        outgoing.setdefault(e.start, set()).add(e.end)
    return graph, nodes, outgoing


def _assert_agent_to_mcp(agent: str, mcp: str, outgoing: dict):
    assert agent in outgoing, f"Agent {agent} missing from edges"
    assert mcp in outgoing[agent], f"Expected edge {agent}->{mcp}"


# ================ Tests =====================

def test_mcp_stdio_detection(analyzer, code_workspace):
    code = """
    import asyncio
    from agents import Agent
    from agents.mcp import MCPServerStdio

    async def main():
        async with MCPServerStdio(name="fs_server", params={"command":"npx","args":["-y","pkg","."]}) as s:
            agent = Agent(name="A1", instructions="i", mcp_servers=[s])
    """
    root = code_workspace({"proj/main.py": code})
    graph, nodes, outgoing = _run(analyzer, root)
    assert "A1" in nodes
    assert "fs_server" in nodes
    assert nodes["fs_server"].node_type == NodeType.MCP_SERVER
    _assert_agent_to_mcp("A1", "fs_server", outgoing)


def test_mcp_sse_detection(analyzer, code_workspace):
    code = """
    import asyncio
    from agents import Agent
    from agents.mcp import MCPServerSse
    async def main():
        async with MCPServerSse(name="sse_srv", params={"url":"http://localhost:8000/sse"}) as sse:
            agent = Agent(name="A2", instructions="i", mcp_servers=[sse])
    """
    root = code_workspace({"proj/sse.py": code})
    graph, nodes, outgoing = _run(analyzer, root)
    assert "A2" in nodes
    assert "sse_srv" in nodes
    assert nodes["sse_srv"].node_type == NodeType.MCP_SERVER
    _assert_agent_to_mcp("A2", "sse_srv", outgoing)


def test_hosted_mcp_tool_detection(analyzer, code_workspace):
    code = """
    from agents import Agent, HostedMCPTool
    hosted_agent = Agent(name="Hosted", instructions="i", tools=[HostedMCPTool(tool_config={"type":"mcp","server_label":"example_server","server_url":"https://example.com/mcp","require_approval":"never"})])
    """
    root = code_workspace({"proj/hosted.py": code})
    graph, nodes, outgoing = _run(analyzer, root)
    # Hosted MCP represented as MCP server node with name from server_label
    assert "Hosted" in nodes
    assert "example_server" in nodes
    assert nodes["example_server"].node_type == NodeType.MCP_SERVER
    _assert_agent_to_mcp("Hosted", "example_server", outgoing)
    # Ensure params JSON includes server_url
    params = json.loads(nodes["example_server"].description)
    assert params.get("server_url") == "https://example.com/mcp"


def test_multiple_servers_async_with(analyzer, code_workspace):
    code = """
    import asyncio
    from agents import Agent
    from agents.mcp import MCPServerStdio, MCPServerStreamableHttp

    async def main():
        async with MCPServerStdio(name="fs1", params={"command":"npx","args":["a"]}) as fs, MCPServerStreamableHttp(name="http1", params={"url":"http://localhost:8002/mcp"}) as http:
            agent = Agent(name="Multi", instructions="i", mcp_servers=[fs, http])
    """
    root = code_workspace({"proj/multi.py": code})
    graph, nodes, outgoing = _run(analyzer, root)
    assert {"fs1", "http1", "Multi"}.issubset(nodes.keys())
    assert nodes["fs1"].node_type == nodes["http1"].node_type == NodeType.MCP_SERVER
    _assert_agent_to_mcp("Multi", "fs1", outgoing)
    _assert_agent_to_mcp("Multi", "http1", outgoing)


def test_git_example_pattern(analyzer, code_workspace):
    code = """
    import asyncio
    from agents import Agent
    from agents.mcp import MCPServerStdio

    async def main():
        async with MCPServerStdio(name="git_srv", params={"command":"uvx","args":["mcp-server-git"]}) as g:
            agent = Agent(name="GitAgent", instructions="Answer git questions", mcp_servers=[g])
    """
    root = code_workspace({"proj/git.py": code})
    graph, nodes, outgoing = _run(analyzer, root)
    assert "GitAgent" in nodes
    assert "git_srv" in nodes
    _assert_agent_to_mcp("GitAgent", "git_srv", outgoing)


def test_assigned_mcp_then_async_with_single(analyzer, code_workspace):
    code = """
    from agents import Agent
    from agents.mcp import MCPServerStdio

    filesystem_server = MCPServerStdio(name="assigned_fs", params={"command":"npx","args":["-y","pkg","."]})

    async def main():
        async with filesystem_server as fs:
            agent = Agent(name="AssignedA", instructions="i", mcp_servers=[fs])
    """
    root = code_workspace({"proj/assigned_single.py": code})
    graph, nodes, outgoing = _run(analyzer, root)
    assert "AssignedA" in nodes
    # Node should have the name passed in constructor (assigned_fs)
    assert "assigned_fs" in nodes
    assert nodes["assigned_fs"].node_type == NodeType.MCP_SERVER
    _assert_agent_to_mcp("AssignedA", "assigned_fs", outgoing)



def test_assigned_multiple_mcp_then_async_with_multiple(analyzer, code_workspace):
    code = """
    from agents import Agent
    from agents.mcp import MCPServerStdio, MCPServerStreamableHttp

    filesystem_server = MCPServerStdio(name="fs_assigned", params={"command":"npx","args":["a"]})
    http_server = MCPServerStreamableHttp(name="http_assigned", params={"url":"http://localhost:9000/mcp"})

    async def main():
        async with filesystem_server as fs, http_server as http:
            agent = Agent(name="AssignedMulti", instructions="i", mcp_servers=[fs, http])
    """
    root = code_workspace({"proj/assigned_multi.py": code})
    graph, nodes, outgoing = _run(analyzer, root)
    assert {"AssignedMulti", "fs_assigned", "http_assigned"}.issubset(nodes.keys())
    _assert_agent_to_mcp("AssignedMulti", "fs_assigned", outgoing)
    _assert_agent_to_mcp("AssignedMulti", "http_assigned", outgoing)
