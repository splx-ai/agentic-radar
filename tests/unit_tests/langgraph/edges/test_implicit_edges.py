from agentic_radar.analysis.langgraph.analyze import LangGraphAnalyzer

import pytest

@pytest.mark.supported
def test_add_node_with_Command_objects_single_return_single_value(tmp_path):
    """
    A test for detecting edges that are implicitly defined by a single returned Command object and its "goto" argument. The "goto" argument is a single value.
    """
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END

def node1(state: GraphState):
  return Command(
        update={
            "foo": "bar"
        },
        goto="node2")

def node2(state: GraphState):
  return "Node2 was visited."

def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)
                       
    workflow.set_entry_point("node1")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    relevant_edge = None

    for edge in graph.edges:
        if edge.start == "node1" and edge.end == "node2" and not edge.condition:
            relevant_edge = edge

    assert len(graph.edges) == 2 and relevant_edge


@pytest.mark.supported
def test_add_node_with_Command_objects_single_return_multiple_values_list(tmp_path):
    """
    A test for detecting edges that are implicitly defined by a single returned Command object and its "goto" argument. 
    The "goto" argument is a list containing multiple values, implicitly making the edges conditional.
    """
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END

def node1(state: GraphState):
  return Command(
        update={
            "foo": "bar"
        },
        goto=["node2", "node3"])

def node2(state: GraphState):
  return "Node2 was visited."
                       
def node3(state: GraphState):
  return "Node3 was visited."

def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)
    workflow.add_node("node3", node3)
                
    workflow.set_entry_point("node1")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    relevant_edge_to_node2 = False
    relevant_edge_to_node3 = False

    for edge in graph.edges:
        if edge.start == "node1" and edge.end == "node2" and edge.condition:
            relevant_edge_to_node2 = True
        elif edge.start == "node1" and edge.end == "node3" and edge.condition:
            relevant_edge_to_node3 = True

    assert len(graph.edges) == 3 and relevant_edge_to_node2 and relevant_edge_to_node3


@pytest.mark.supported
def test_add_node_with_Command_objects_single_return_multiple_values_conditional(tmp_path):
    """
    A test for detecting edges that are implicitly defined by a single returned Command object and its "goto" argument.
    The "goto" argument is a single variable that can have more than one value, making the edges implicitly conditional.
    """
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END
from random import random

def node1(state: GraphState):
  goto = "node2"
  if random() < 0.5:
    goto = "node3"
  return Command(
        update={
            "foo": "bar"
        },
        goto=goto)

def node2(state: GraphState):
  return "Node2 was visited."
                       
def node3(state: GraphState):
  return "Node3 was visited."

def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)
    workflow.add_node("node3", node3)
                
    workflow.set_entry_point("node1")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    relevant_edge_to_node2 = False
    relevant_edge_to_node3 = False

    for edge in graph.edges:
        if edge.start == "node1" and edge.end == "node2" and edge.condition:
            relevant_edge_to_node2 = True
        elif edge.start == "node1" and edge.end == "node3" and edge.condition:
            relevant_edge_to_node3 = True

    assert len(graph.edges) == 3 and relevant_edge_to_node2 and relevant_edge_to_node3


@pytest.mark.supported
def test_add_node_with_Command_objects_multiple_returns_multiple_values_conditional(tmp_path):
    """
    A test for detecting edges that are implicitly defined by multiple returned Command objects and their "goto" arguments.
    The "goto" arguments are single values, but since there are multiple returned Command object the edges are conditional.
    """
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END
from random import random

def node1(state: GraphState):
  goto = "node2"
  if random() < 0.5:
    return Command(
            update={
                "foo": "bar"
            },
            goto="node2")
  else:
    return Command(
            update={
                "foo": "bar"
            },
            goto="node3")

def node2(state: GraphState):
  return "Node2 was visited."
                       
def node3(state: GraphState):
  return "Node3 was visited."

def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)
    workflow.add_node("node3", node3)
                
    workflow.set_entry_point("node1")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    relevant_edge_to_node2 = False
    relevant_edge_to_node3 = False

    for edge in graph.edges:
        if edge.start == "node1" and edge.end == "node2" and edge.condition:
            relevant_edge_to_node2 = True
        elif edge.start == "node1" and edge.end == "node3" and edge.condition:
            relevant_edge_to_node3 = True

    assert len(graph.edges) == 3 and relevant_edge_to_node2 and relevant_edge_to_node3