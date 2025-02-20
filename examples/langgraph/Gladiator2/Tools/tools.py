import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.tools import TavilySearchResults
from langchain_community.utilities.jira import JiraAPIWrapper

from Tools.helper import LegalDocumentsVectorStore
from Tools.create_tools import create_retriever_tool, create_employee_db_tool, create_jira_tool, generate_document_parsed_input_json_tool

load_dotenv()

embeddings_huggingface = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

tavily_search = TavilySearchResults(
    max_results=3,
    include_answer=True,
    include_raw_content=True,
    include_images=True,
    description="A search engine optimized for comprehensive, accurate, and trusted results. Useful for when you need to answer questions about legal stuff, laws and the rest of the stuff for generating response about terms and conditions of companies, data privacy and company's organization. Input should be a search query."
)

jira_instance = JiraAPIWrapper(
    jira_api_token = os.getenv('JIRA_API_TOKEN'),
    jira_instance_url = os.getenv('JIRA_INSTANCE_URL'),
    jira_username = os.getenv('JIRA_USERNAME'))

directory = os.path.join(os.getcwd(), 'input_files', 'supplier_liability_contracts')
save_directory = os.path.join(os.getcwd(), 'output_files', 'supplier_liability_contracts')

legal_documents = [os.path.join(directory, path) for path in os.listdir(directory) if path.endswith('.docx')]

legal_docs_vector_store_class = LegalDocumentsVectorStore(legal_documents=legal_documents, embeddings=embeddings_huggingface)
vector_store_instance = legal_docs_vector_store_class.get_vector_store()
retrieval_params = {
    'search_type':"mmr",
    'search_kwargs':{"k": 3}}
legal_docs_retriever_tool = create_retriever_tool(vector_store_instance, retrieval_params)
employee_db_tool = create_employee_db_tool(db=os.path.join(os.getcwd(), 'input_files', 'employees.db'))
jira_search_tool = create_jira_tool(jira_instance, tool_type='search')
jira_create_tool = create_jira_tool(jira_instance, tool_type='create')

tools = [tavily_search, legal_docs_retriever_tool, employee_db_tool, jira_search_tool, generate_document_parsed_input_json_tool] #, jira_create_tool]
