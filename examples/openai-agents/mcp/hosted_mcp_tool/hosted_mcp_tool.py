from agents import Agent, CodeInterpreterTool, FileSearchTool, WebSearchTool, HostedMCPTool

# Agent with hosted tools
research_agent = Agent(
    name="Research Assistant",
    instructions="You help with research using web search and file retrieval",
    tools=[
        WebSearchTool(),
        FileSearchTool(
            vector_store_ids=["vs_example123"],
            max_num_results=5,
        ),
        CodeInterpreterTool(),
    ],
)

# Agent with MCP tools
mcp_agent = Agent(
    name="MCP Assistant",
    instructions="You use Model Context Protocol tools",
    tools=[
        HostedMCPTool(
            tool_config={
                "type": "mcp",
                "server_label": "example_server",
                "server_url": "https://example.com/mcp",
                "require_approval": "never",
            }
        ),
    ],
)