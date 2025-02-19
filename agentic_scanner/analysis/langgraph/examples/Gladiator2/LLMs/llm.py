import os
import boto3
from botocore.config import Config

from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langchain_aws import ChatBedrock

from Tools.tools import tools
load_dotenv()

azure_llm = AzureChatOpenAI(
    deployment_name="gpt-3",
    model_name="gpt-3 1106",
    api_version="2023-06-01-preview",
    streaming=True)
azure_llm = azure_llm.bind_tools(tools)

boto3_session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key= os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)
bedrock_client = boto3_session.client("bedrock-runtime", config=Config(region_name=os.getenv('AWS_REGION')))
aws_llm = ChatBedrock(
    model_id = 'meta.llama3-1-8b-instruct-v1:0',
    client = bedrock_client
)
