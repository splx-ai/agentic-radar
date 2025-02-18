from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph import MessagesState, StateGraph
from typing_extensions import TypedDict
from typing import List, Annotated

class GraphState(TypedDict):
    initial_prompt: str
    # add_messages connects mesages to list if they have different IDs
    # AnyMessage - it can be AI or Human
    messages: Annotated[List[AnyMessage], add_messages]
    num_steps: int
    final_doc: str
    thread_id: str
    result: str
    document_template: str
    created_jira_ticket: dict
