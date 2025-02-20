import json

from langchain_core.messages import SystemMessage
from langgraph.types import Command

from langchain_core.runnables import RunnableConfig

from LLMs.llm import azure_llm
from nodes.state import GraphState
from Tools.tools import tools
from prompts.prompts import research_prompt

tools_by_name = {tool.name: tool for tool in tools}

# Define the node that calls the model
def call_model(
        state: GraphState,
        config: RunnableConfig,
    ):
    # this is similar to customizing the create_react_agent with state_modifier, but is a lot more flexible
    system_prompt = SystemMessage(
        research_prompt
    )

    print(f"Last message azure llm: {state['messages'][-1]}")

    last_message = state['messages'][-1]
    last_message_name = None
    try:
        last_message_name = last_message.name
    except Exception as e:
        print(f'Error ocurred: {e}')
        pass
    if last_message_name and last_message_name == 'generate_document_parsed_input_json':
        return Command(
        # here can be either result["messages"] - if we want to share entire history, either result["messages"][-1] if we
        # want to share only last part
        update={
            "document_template": json.loads(last_message.content),
            "num_steps": state['num_steps'] + 1,
        },
        goto='generator')

    response = azure_llm.invoke([system_prompt] + state["messages"], config)
    # We return a list, because this will get added to the existing list
    state["messages"] = state['messages'] + [response]
    # print(state)
    goto = get_next_node_researcher(state, "output_node")

    return Command(
        # here can be either result["messages"] - if we want to share entire history, either result["messages"][-1] if we
        # want to share only last part
        update={
            "num_steps": state['num_steps'] + 1,
            "messages": state['messages']
        },
        goto=goto)

def get_next_node_researcher(state: GraphState, goto: str):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return 'tools'
    else:
        return goto