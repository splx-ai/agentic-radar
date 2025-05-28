from agentic_radar.analysis.langgraph.analyze import LangGraphAnalyzer
from agentic_radar.graph import NodeType

import pytest

@pytest.mark.supported
def test_agent_nodes(tmp_path):
    """
    Test that the analyzer correctly identifies agent nodes in a minimal LangGraph setup.
    """
    # Create a minimal Python file with an agent node (llm.bind_tools and invoke)
    py_file = tmp_path / "test_file.py"
    py_file.write_text('''
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END
from langchain_openai import ChatOpenAI

class GraphState:
    pass

class Command:
    def __init__(self, update, goto):
        self.update = update
        self.goto = goto

def agent_node(state: GraphState):
    llm = ChatOpenAI(model="gpt-4o")
    llm = llm.bind_tools([])
    return llm.invoke(["hello"])

def basic_node(state: GraphState):
    return "not agent"

def input_node(state: GraphState):
    return Command(
        update={
            "initial_prompt": state.__dict__ if hasattr(state, "__dict__") else {},
            "num_steps": 0
        },
        goto=END,
    )

def create_workflow():
    workflow = StateGraph(GraphState)
    workflow.add_node("agent_node", agent_node)
    workflow.add_node("basic_node", basic_node)
    workflow.add_node("input_node", input_node)
    workflow.set_entry_point("input_node")
    return workflow.compile()
''')

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))
    print(graph)
    agent_nodes = [n for n in graph.nodes if n.node_type == NodeType.AGENT]

    # There should be exactly one agent node and one basic node (plus START/END)
    assert len(agent_nodes) == 1
    assert len([n for n in graph.nodes if n.node_type == NodeType.BASIC and n.name == "basic_node"]) == 1
    # The agent should also be in the agents field, and match exactly
    assert len(graph.agents) == 1
    assert graph.agents[0].name == agent_nodes[0].name
    # START and END nodes should always be present
    assert any(n.name == "START" for n in graph.nodes)
    assert any(n.name == "END" for n in graph.nodes)

    # The agent's llm and system_prompt should be empty strings
    agent = graph.agents[0]
    assert agent.llm == ""
    assert agent.system_prompt == ""
    assert agent.is_guardrail is False
    assert agent.vulnerabilities == []
