import os
from crewai import Agent, Task, Crew
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters # For Stdio Server

# Example server_params (choose one based on your server type):
# 1. Stdio Server:
server_params=StdioServerParameters(
    command="python3",
    args=["servers/your_server.py"],
    env={"UV_PYTHON": "3.12", **os.environ},
)

# 2. SSE Server:
server_params = {
    "url": "http://localhost:8000/sse",
    "transport": "sse"
}

# 3. Streamable HTTP Server:
server_params = {
    "url": "http://localhost:8001/mcp",
    "transport": "streamable-http"
}

# Example usage (uncomment and adapt once server_params is set):
with MCPServerAdapter(server_params, connect_timeout=60) as mcp_tools:
    print(f"Available tools: {[tool.name for tool in mcp_tools]}")

    my_agent = Agent(
        role="MCP Tool User",
        goal="Utilize tools from an MCP server.",
        backstory="I can connect to MCP servers and use their tools.",
        tools=mcp_tools, # Pass the loaded tools to your agent
        reasoning=True,
        verbose=True
    )
    # Minimal Task using the agent and MCP tools
    list_tools_task = Task(
        description="List the available MCP tools and provide a short description for each.",
        expected_output="A bullet list of tool names with their descriptions.",
        agent=my_agent
    )

    # Minimal Crew tying it together
    crew = Crew(
        agents=[my_agent],
        tasks=[list_tools_task],
        verbose=True
    )

    if __name__ == "__main__":
        result = crew.kickoff()
        print("\nCrew result:\n", result)