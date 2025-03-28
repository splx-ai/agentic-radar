from agentic_radar.analysis.langgraph.analyze import LangGraphAnalyzer

import pytest

@pytest.mark.supported
def test_add_node_with_name_and_with_function_name(tmp_path):
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END

def input_node(state: GraphState):
  return Command(
      update={
          "initial_prompt": state["messages"],
          "num_steps": 0
      },
      goto=END,
  )

def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("input_node", input_node)
                       
    workflow.set_entry_point("input_node")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    assert (len(graph.nodes) == 3) and ("input_node" in [node.name for node in graph.nodes])

@pytest.mark.supported
def test_add_node_without_name_and_with_function_name(tmp_path):
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END

def input_node(state: GraphState):
  return Command(
      update={
          "initial_prompt": state["messages"],
          "num_steps": 0
      },
      goto=END,
  )

def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node(input_node)
                       
    workflow.set_entry_point("input_node")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")
    
    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    assert (len(graph.nodes) == 3) and ("input_node" in [node.name for node in graph.nodes])


@pytest.mark.supported
def test_add_node_with_name_and_with_function_call(tmp_path):
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END

def input_node(state: GraphState):
  return Command(
      update={
          "initial_prompt": state["messages"],
          "num_steps": 0
      },
      goto=END,
  )

def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("input_node", input_node())
                       
    workflow.set_entry_point("input_node")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
""")

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    assert (len(graph.nodes) == 3) and ("input_node" in [node.name for node in graph.nodes])