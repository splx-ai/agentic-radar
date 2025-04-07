from agentic_radar.analysis.langgraph.analyze import LangGraphAnalyzer

import pytest

@pytest.mark.supported
def test_add_edge_positional_arguments(tmp_path):
    """
    Positional arguments in "add_edge".
    """
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END

def node1(state: GraphState):
  return "Node1 was visited."

def node2(state: GraphState):
  return "Node2 was visited."

def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)

    workflow.add_edge("node1", "node2")
                       
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
def test_add_edge_keyword_arguments(tmp_path):
    """
    Keyword arguments in "add_edge".
    """
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END

def node1(state: GraphState):
  return "Node1 was visited."

def node2(state: GraphState):
  return "Node2 was visited."

def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)

    workflow.add_edge(start_key="node1", end_key="node2")
                       
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
def test_add_conditional_edges_keyword_arguments_without_map_local(tmp_path):
    """
    Keyword arguments in "add_conditional_edges". Routing function not imported.
    """
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END
                       
from random import random

def route_function(
    state: State,
):
    
    if random() < 0.5:
      return END
    else:
      return "node2"

def node1(state: GraphState):
  return "Node1 was visited."

def node2(state: GraphState):
  return "Node2 was visited."


def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)

    workflow.add_conditional_edges(source="node1", path=route_function)
                       
    workflow.set_entry_point("node1")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    conditional_edge_to_END = False
    conditional_edge_to_node2 = False

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "END":
          conditional_edge_to_END = True

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "node2":
          conditional_edge_to_node2 = True

    assert (len(graph.edges) == 3) and conditional_edge_to_END and conditional_edge_to_node2


@pytest.mark.supported
def test_add_conditional_edges_keyword_arguments_without_map_imported(tmp_path):
    """
    Keyword arguments in "add_conditional_edges". Routing function imported.
    """
    py_file_1 = tmp_path / "test_file_1.py"
    py_file_1.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END
                         
from test_file_2 import route_function
                       
from random import random

def node1(state: GraphState):
  return "Node1 was visited."

def node2(state: GraphState):
  return "Node2 was visited."


def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)

    workflow.add_conditional_edges(source="node1", path=route_function)
                       
    workflow.set_entry_point("node1")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    py_file_2 = tmp_path / "test_file_2.py"
    py_file_2.write_text("""
from langgraph.graph import END

def route_function(
    state: State,
):
    
    if random() < 0.5:
      return END
    else:
      return "node2"
""")


    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    conditional_edge_to_END = False
    conditional_edge_to_node2 = False

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "END":
          conditional_edge_to_END = True

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "node2":
          conditional_edge_to_node2 = True

    assert (len(graph.edges) == 3) and conditional_edge_to_END and conditional_edge_to_node2


@pytest.mark.supported
def test_add_conditional_edges_positional_arguments_without_map_local(tmp_path):
    """
    Positional arguments in "add_conditional_edges". Routing function not imported.
    """
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END
                       
from random import random

def route_function(
    state: State,
):
    
    if random() < 0.5:
      return END
    else:
      return "node2"

def node1(state: GraphState):
  return "Node1 was visited."

def node2(state: GraphState):
  return "Node2 was visited."


def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)

    workflow.add_conditional_edges("node1", route_function)
                       
    workflow.set_entry_point("node1")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    conditional_edge_to_END = False
    conditional_edge_to_node2 = False

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "END":
          conditional_edge_to_END = True

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "node2":
          conditional_edge_to_node2 = True

    assert (len(graph.edges) == 3) and conditional_edge_to_END and conditional_edge_to_node2


@pytest.mark.supported
def test_add_conditional_edges_positional_arguments_without_map_imported(tmp_path):
    """
    Positional arguments in "add_conditional_edges". Routing function imported.
    """
    py_file_1 = tmp_path / "test_file_1.py"
    py_file_1.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END
                         
from test_file_2 import route_function

def node1(state: GraphState):
  return "Node1 was visited."

def node2(state: GraphState):
  return "Node2 was visited."


def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)

    workflow.add_conditional_edges("node1", route_function)
                       
    workflow.set_entry_point("node1")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    py_file_2 = tmp_path / "test_file_2.py"
    py_file_2.write_text("""
from langgraph.graph import END
from random import random

def route_function(
    state: State,
):
    
    if random() < 0.5:
      return END
    else:
      return "node2"
""")


    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    conditional_edge_to_END = False
    conditional_edge_to_node2 = False

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "END":
          conditional_edge_to_END = True

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "node2":
          conditional_edge_to_node2 = True

    assert (len(graph.edges) == 3) and conditional_edge_to_END and conditional_edge_to_node2



@pytest.mark.supported
def test_add_conditional_edges_keyword_arguments_with_map_local(tmp_path):
    """
    Keyword arguments in "add_conditional_edges". Path mapping not imported.
    """
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END
                       
from random import random

def route_function(
    state: State,
):
    
    if random() < 0.5:
      return 1
    else:
      return 2

mapping = {
        1: END,
        2: "node2"
}

def node1(state: GraphState):
  return "Node1 was visited."

def node2(state: GraphState):
  return "Node2 was visited."


def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)

    workflow.add_conditional_edges(source="node1", path=route_function, path_map=mapping)
                       
    workflow.set_entry_point("node1")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    conditional_edge_to_END = False
    conditional_edge_to_node2 = False

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "END":
          conditional_edge_to_END = True

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "node2":
          conditional_edge_to_node2 = True

    assert (len(graph.edges) == 3) and conditional_edge_to_END and conditional_edge_to_node2


@pytest.mark.supported
def test_add_conditional_edges_keyword_arguments_with_map_imported(tmp_path):
    """
    Keyword arguments in "add_conditional_edges". Path mapping imported.
    """
    py_file_1 = tmp_path / "test_file_1.py"
    py_file_1.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END
                         
from test_file_2 import route_function, mapping

def node1(state: GraphState):
  return "Node1 was visited."

def node2(state: GraphState):
  return "Node2 was visited."


def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)

    workflow.add_conditional_edges(source="node1", path=route_function, path_map=mapping)
                       
    workflow.set_entry_point("node1")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    py_file_2 = tmp_path / "test_file_2.py"
    py_file_2.write_text("""
from langgraph.graph import END
from random import random

def route_function(
    state: State,
):
    
    if random() < 0.5:
      return 1
    else:
      return 2

mapping = {
        1: END,
        2: "node2"
}
""")


    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    conditional_edge_to_END = False
    conditional_edge_to_node2 = False

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "END":
          conditional_edge_to_END = True

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "node2":
          conditional_edge_to_node2 = True

    assert (len(graph.edges) == 3) and conditional_edge_to_END and conditional_edge_to_node2


@pytest.mark.supported
def test_add_conditional_edges_positional_arguments_with_map_local(tmp_path):
    """
    Positional arguments in "add_conditional_edges". Path mapping not imported.
    """
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END
                       
from random import random

def route_function(
    state: State,
):
    
    if random() < 0.5:
      return 1
    else:
      return 2

mapping = {
        1: END,
        2: "node2"
}

def node1(state: GraphState):
  return "Node1 was visited."

def node2(state: GraphState):
  return "Node2 was visited."


def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)

    workflow.add_conditional_edges("node1", route_function, mapping)
                       
    workflow.set_entry_point("node1")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    conditional_edge_to_END = False
    conditional_edge_to_node2 = False

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "END":
          conditional_edge_to_END = True

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "node2":
          conditional_edge_to_node2 = True

    assert (len(graph.edges) == 3) and conditional_edge_to_END and conditional_edge_to_node2


@pytest.mark.supported
def test_add_conditional_edges_positional_arguments_with_map_imported(tmp_path):
    """
    Positional arguments in "add_conditional_edges". Path mapping imported.
    """
    py_file_1 = tmp_path / "test_file_1.py"
    py_file_1.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END
                         
from test_file_2 import route_function, mapping

def node1(state: GraphState):
  return "Node1 was visited."

def node2(state: GraphState):
  return "Node2 was visited."


def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)

    workflow.add_conditional_edges("node1", route_function, mapping)
                       
    workflow.set_entry_point("node1")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    py_file_2 = tmp_path / "test_file_2.py"
    py_file_2.write_text("""
from langgraph.graph import END
from random import random

def route_function(
    state: State,
):
    
    if random() < 0.5:
      return 1
    else:
      return 2

mapping = {
        1: END,
        2: "node2"
}
""")


    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    conditional_edge_to_END = False
    conditional_edge_to_node2 = False

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "END":
          conditional_edge_to_END = True

    for edge in graph.edges:
        if edge.condition is not None and edge.start == "node1" and edge.end == "node2":
          conditional_edge_to_node2 = True

    assert (len(graph.edges) == 3) and conditional_edge_to_END and conditional_edge_to_node2