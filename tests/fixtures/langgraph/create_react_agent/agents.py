from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI


def tavily_tool(query):
    """Search tool"""
    pass


def python_repl_tool(code):
    """Python execution tool"""
    pass


def bash_tool(command):
    """Bash execution tool"""
    pass


# Pattern 1: create_react_agent with tools list
research_agent = create_react_agent(
    ChatOpenAI(model="gpt-4"),
    tools=[tavily_tool],
)

# Pattern 2: create_react_agent with multiple tools
coder_agent = create_react_agent(
    ChatOpenAI(model="gpt-4"),
    tools=[python_repl_tool, bash_tool],
)

# Pattern 3: create_react_agent with prompt
browser_agent = create_react_agent(
    ChatOpenAI(model="gpt-4"),
    tools=[],
    prompt="You are a browser automation agent",
)
