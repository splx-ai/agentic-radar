import json

from langchain_core.messages import ToolMessage
from langgraph.graph import END
from langgraph.types import Command

from nodes.state import GraphState
from Tools.tools import tools, legal_docs_vector_store_class

tools_by_name = {tool.name: tool for tool in tools}


def tool_node(state: GraphState):
    outputs = []
    for tool_call in state["messages"][-1].tool_calls:
        try:
            tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        except Exception as e:
            return Command(
                update = {
                    "num_steps": state['num_steps'] + 1,
                    "messages": state['messages'] + [
                        ToolMessage(
                            content=f"Error: {repr(e)}\n please fix your mistakes.",
                            tool_call_id=tool_call["id"],
                        )
                    ]
                },
                goto='researcher')
    return Command(
        # here can be either result["messages"] - if we want to share entire history, either result["messages"][-1] if we
        # want to share only last part
        update={
            # share internal message history of research agent with other agents
            "num_steps": state["num_steps"] + 1,
            "messages": state['messages'] + outputs,
        },
        goto='researcher')


def output_node(state: GraphState):
  legal_docs_vector_store_class.delete_documents()

  try:
     output_message = state["messages"][-1].content
  except Exception as e:
     output_message = state["messages"][-1]
  return Command(
      update={
          "result": output_message
      },
      goto=END,
  )

def input_node(state: GraphState):
  legal_docs_vector_store_class.add_documents()
  return Command(
      update={
          "initial_prompt": state["messages"],
          "num_steps": 0
      },
      goto="researcher",
  )

