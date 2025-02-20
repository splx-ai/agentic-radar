import json
import os
from dotenv import load_dotenv

from langchain_core.messages import SystemMessage
from langgraph.types import Command
from langgraph.graph import END

from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate

from LLMs.llm import aws_llm
from nodes.state import GraphState
from Tools.tools import save_directory, jira_create_tool, legal_docs_vector_store_class
from Tools.helper import save_document, retrieve_whole_document

load_dotenv()

def generate_document_node(state: GraphState):
    system_prompt = SystemMessage(
        """
        You are a highly experienced legal assistant AI. 
        Follow all instructions carefully and produce well-structured legal content.
        Use formal language and number sections clearly. Also, divide sections with "\n\n".
        Each chapter can have with length of maximum 500 characters.
        It can be maximum of 10 chapters in each document.
        """
    )
    print(state['document_template'])
    if isinstance(state['document_template'], str):
        document_template_input_dictionary = json.loads(state['document_template'])
    else:
        document_template_input_dictionary = state['document_template']

    required_action = document_template_input_dictionary['action']
    print(f"Required action: {required_action}")

    if required_action not in ['generate_new', 'add_chapter']:
        if 'title' in document_template_input_dictionary.keys():
            required_action = 'generate_new'
        else:
            required_action = 'add_chapter'

    if required_action == 'generate_new':
        human_message = HumanMessagePromptTemplate.from_template(
            """
            Your task is to generate the new document using document template defined here:
            Title: {title}

            Write multiple chapters,on the following topic - {topic}, where supplier is {supplier} and retrived information from WEB and local database is here: {retrieved_information}.

            If it seems useful to you, use the informations defined here: {retrieved_information}.
            
            Please, as a result content only have document text as I am looking to save it directly to document.
            """
        )
    elif required_action == 'add_chapter':
        human_message = HumanMessagePromptTemplate.from_template(
            """
            Your task is adding a chapter in the existing document. Use document template defined here:
            {existing_content}

            Write a new chapter on the following topic, where supplier is {supplier} and retrived information from WEB and local database is here: {retrieved_information}:
            Chapter: {topic}

            If it seems useful to you, use the informations defined here: {retrieved_information}.

            Please, as a result content only have document text as I am looking to save it directly to document.
            """
        )
        document_template_input_dictionary['existing_content'] = retrieve_whole_document(legal_docs_vector_store_class, document_template_input_dictionary['supplier'])

    chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_message])

    result = aws_llm.invoke(chat_prompt.invoke(document_template_input_dictionary))

    supplier = document_template_input_dictionary['supplier']
    title = document_template_input_dictionary['title']

    if supplier.lower() in title.lower():
        path = title.lower().replace(' ', '_') + '_ai_created.docx'
    else:
        path = title.lower().replace(' ', '_') + f'_with_{supplier.lower()}_ai_created.docx'

    response = save_document(result.content, os.path.join(save_directory, path))
    if response == -1:
        output_message = f"""Required document already exists on the path: {path}."""
        return Command(
            update={
                "result": output_message,
                "num_steps": state['num_steps'] + 1
            },
            goto=END
        )

    issue_data = {
        'project': { 'key': os.getenv('JIRA_project_key')},
        'summary': 'Create new supplier doc',
        'description': f'Creating review ticket for newly generated document on supplier liability contract at the following path: {path}',
        'issuetype': {'name': 'Task'}
    }
    try:
        result = jira_create_tool.invoke(json.dumps(issue_data))
    except Exception as e:
        result = f"Tried creating a ticket, but the following error occurred: {e}\n."
    # TODO return result after fixing JIRA problem

    output_message = f"""Created new document with path: {path}."""

    return Command(
        update={
            "result": output_message,
            "created_jira_ticket": issue_data,
            "final_doc": path,
            "messages": [output_message],
            "num_steps": state['num_steps'] + 1
        },
        goto=END
    )
