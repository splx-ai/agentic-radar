from agents import MCPServerStdio, MCPServerStreamableHttp, Agent, ModelSettings, function_tool

@function_tool
def get_weather(location: str) -> str:
    """Fetches the current weather for a given location."""
    return f"The current weather in {location} is sunny with a temperature of 75°F."

@function_tool
def calculate(expression: str) -> str:
    """Calculates a mathematical expression."""
    try:
        result = eval(expression)
        return f"The result of {expression} is {result}."
    
    except Exception as e:
        return f"Error calculating expression: {e}"
    
@function_tool
def fetch_stock_price(ticker: str) -> str:
    """Fetches the current stock price for a given ticker symbol."""
    return f"The current stock price of {ticker} is $150.00."

# Agent with multiple MCP servers (single async with with multiple as)
filesystem_server = MCPServerStdio(
    name="multi_filesystem_server",
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
    },
)

http_multi_server = MCPServerStreamableHttp(
    name="multi_http_server",
    params={
        "url": "http://localhost:8002/mcp",
    },
    tool_filter=dynamic_filter,
)

async with filesystem_server as fs_srv, http_multi_server as http_srv:
    multi_agent = Agent(
        name="Multi MCP Agent",
        instructions="Use multiple MCP servers for comprehensive operations.",
        mcp_servers=[fs_srv, http_srv], # NOT DETECTED
        tools=[get_weather, calculate, fetch_stock_price],
        model_settings=ModelSettings(tool_choice="required"),
    )
    agents.append(multi_agent)