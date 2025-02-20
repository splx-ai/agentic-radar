from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from nodes.nodes import tool_node, input_node, output_node
from nodes.researcher import call_model
from nodes.generator import generate_document_node
from nodes.state import GraphState

# from example.dicts import dictionary2
# from example.func import function


# def route_update_flight(
#     state: State,
# ):
#     route = tools_condition(state)
#     if route == END:
#         return END
#     tool_calls = state["messages"][-1].tool_calls
#     did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
#     if did_cancel:
#         return "leave_skill"
#     safe_toolnames = [t.name for t in update_flight_safe_tools]
#     if all(tc["name"] in safe_toolnames for tc in tool_calls):
#         return "update_flight_safe_tools"
#     return "update_flight_sensitive_tools"


# def route_update_flight2(
#     state: State,
# ):
#     route = tools_condition(state)

#     return_node = "update_flight_sensitive_tools"
#     if route == END:
#         return_node = END
#     tool_calls = state["messages"][-1].tool_calls
#     did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
#     if did_cancel:
#         return_node = "leave_skill"
#     safe_toolnames = [t.name for t in update_flight_safe_tools]
#     if all(tc["name"] in safe_toolnames for tc in tool_calls):
#         return_node = "update_flight_safe_tools"
#     return return_node


def create_workflow():
    workflow = StateGraph(GraphState)

    dictionary = {
        "a":"b",
        "c":"d"
    }
    workflow.add_node("input_node", input_node)
    workflow.add_node("researcher", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_node("generator", generate_document_node)
    workflow.add_node("output_node", output_node)
    # workflow.add_node("output2", function())
    # workflow.add_node(output_node)
    # workflow.add_node(output_node())
    # workflow.add_edge("node4", end_key="node5")
    # workflow.add_edge(start_key="node1", end_key="node2")
    # workflow.add_conditional_edges(source="node1", path=route_update_flight)
    # workflow.add_conditional_edges("node2", route_update_flight2)
    # workflow.add_conditional_edges("node3", route_update_flight, ["aaaa", "bbbb"])
    # workflow.add_conditional_edges("node4", route_update_flight, dictionary)
    # workflow.add_conditional_edges("node5", route_update_flight, dictionary2)
    # workflow.add_conditional_edges("node6", function)

    workflow.set_entry_point("input_node")
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
