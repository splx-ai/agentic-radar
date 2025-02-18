from contextlib import closing
import sqlite3
import json

from langchain_community.utilities.jira import JiraAPIWrapper
from langchain.tools import tool

from Tools.helper import LegalDocumentsVectorStore

@tool('generate_document_parsed_input_json', parse_docstring=True)
def generate_document_parsed_input_json_tool(query):
    """Tool for generating JSON structured input to generator node.
    If you have to append existing or generate new document, return json should have following fields:
        - 'title': string, represents title for the new supplier liability contract, None if agent is only appending existing document. Should have supplier in it.
        - 'topic': string, represents topic for new chapter if appending existing document ot topic for new document if generating new document.
        - 'supplier': string, name of the supplier
        - 'retrieved_information': string, information gathered from other tools that will help with creating new document/chapter
        - 'action': string, either 'generate_new' or 'add_chapter', depending on which action should generator node perform

    Parameters
    ----------
    query : str
        Dictionary in string format with specified keys.

    Returns
    -------
    str
        Path where the file has been saved.
    """
    try:
        result = json.loads(query)
    except Exception as e:
        if isinstance(query, dict):
            result = query
        else:
            print(f'Error occurred: {e}\n')
    print(f'\nParser result: {result}\n') 
    return json.dumps(result)


def create_retriever_tool(vector_store: LegalDocumentsVectorStore, retrieval_params: dict = None):
    """
    Factory function to create a custom retriever tool with the given parameters.

    Args:
        vector_store (VectorStore): The vector store instance for document retrieval.
        retrieval_params (dict): Optional parameters for retrieval behavior.

    Returns:
        Callable: A tool decorated with @tool that uses the specified vector store.
    """

    retrieval_params = retrieval_params or {}  # Default to empty dict if not provided

    @tool('retrieve_legal_documents', parse_docstring=True) # response_format je ovdje dobar
    def retriever_tool(query):
        """Retriever for legal documents. Mostly, they are
        supplier liability contracts between SplxAI and its
        suppliers. The retriever is based on the Pinecone
        vector store. Each document is splitted into chunks
        and each chunk is embedded into a 768-dimensional
        vector. The retriever uses the cosine similarity
        metric to retrieve the most similar documents to the
        query. The retriever uses the MMR (Maximal Marginal
        Relevance) search type to retrieve the most relevant
        documents to the query. Each document has in its metadata
        argument its source document whose name represents type of document
        and supplier name.

        Parameters
        ----------
        query : str
            Input query.

        Returns
        -------
        List[Docs]
            List of documents that are most similar to the input query.
        """
        retriever = vector_store.as_retriever(
            search_type=retrieval_params.get('search_type', "mmr"),
            search_kwargs=retrieval_params.get('search_kwargs', {"k": 2})
        )
        results = retriever.invoke(query)
        return "\n\n".join([doc.page_content for doc in results])

    return retriever_tool
    

def create_employee_db_tool(db: str = 'employees.db'):
    """
    Factory function to create a custom SQL database tool with the given database name.

    Args:
        db (str): The database instance name.

    Returns:
        Callable: A tool decorated with @tool that uses the specified SQL database.
    """
    @tool("run_SQL_query", parse_docstring=True)
    def run_query(query: str):
        """Runs SQL query on database employees.db where all the data on
        employees from SplxAI company is stored.
        Columns are id, name, role, email, age
        and gender of employees.

        Args:
            query (str): SQL query to be executed on the specified database.

        Returns
            List: List of tuples that represent the results of the query.
        """
        with closing(sqlite3.connect(db)) as connection:
            with closing(connection.cursor()) as cursor:

                execution_result = cursor.execute(query).fetchall()

        return execution_result
    
    return run_query


def create_jira_tool(jira_instance: JiraAPIWrapper, tool_type: str = 'search'):
    """
    Factory function to create a custom Jira tool with the given Jira instance.
    Tool is based on argument tool_type specified for searching/creating JIRA
    issues.

    Args:
        jira_instance (JiraAPIWrapper): The Jira instance for searching issues.

    Returns:
        Callable: A tool decorated with @tool that uses the specified Jira instance.
    """
    if tool_type == 'search':
        @tool("search_JIRA_issue", parse_docstring=True)
        def search_issue(query: str):
            """Search for issues on JIRA board.
            Some important values here are project key,
            assignee, summary and filter. The input is
            in form of JQL string - query designed specifically
            for JIRA search. Query is surrounded with triple quotes from both sides.

            Args:
                query (str): JQL string - query designed specifically for JIRA search. The examples of JQL string are: "project = 'My Project' and status = 'In progress'";
                "project = 'My Project2' and status = 'Done' and assignee = currentUser". Query is surrounded with triple quotes from both sides.

            Returns
                List: List of issues that match the input query.
            """
            return jira_instance.search(query)
    
        return search_issue
    
    elif tool_type == 'create':
        @tool('create_JIRA_issue', parse_docstring=True)
        def create_issue(jql_str: str):
            """Create an issue on JIRA board for project specified with environment variable or retrieved with search issue tool, with aim to review document generated
            by previous state and with path existing in the current graph state
            Also, if known, specify assignee. The input is in form of json with fields needed
            for creating an issue which are project and description.

            Args:
                jql_str (str): json string - with fields needed for creating an issue.

            Returns
                str: Return notice about created issue.
            """
            try:
                return jira_instance.issue_create(query=jql_str)
            except Exception as e:
                print(f'Error while creating JIRA issue: {e}')
                return f'JIRA issue successfully created.'
            
        return create_issue
    
    else:
        return None
