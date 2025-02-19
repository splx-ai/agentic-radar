import os
import uuid
from IPython.display import Image, display
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

import streamlit as st

from prompts.prompts import sys_msg
from graph import create_workflow

if __name__ == '__main__':
    
    graph = create_workflow()

    try:
        display(Image(graph.get_graph().draw_mermaid_png()))
    except Exception:
        pass

    thread_id = str(uuid.uuid4())

    # I can add here different things that I want to add
    config = {
        "configurable": {
            # Checkpoints are accessed by thread_id
            "thread_id": thread_id,
        }
    }

    prompt = sys_msg
    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)
        with st.chat_message('assistant'):
            st_callback = StreamlitCallbackHandler(st.container())
            for result in graph.stream(
                        {
                            "messages": [
                                    "user",
                                    prompt
                            ],
                        },
                        # Maximum number of steps to take in the graph - check hot connect this to 5
                        config = {
                            "recursion_limit": 50,
                            "configurable": {
                                # Checkpoints are accessed by thread_id
                                "thread_id": thread_id,
                            }
                        },
                        stream_mode='values'
                    ):
                final_result = result
            st.write(final_result['result'])
            if result.get('created_jira_ticket', 0) != 0:
                st.write(f"\nCreated jira ticket with following parameters: {result['created_jira_ticket']}")
