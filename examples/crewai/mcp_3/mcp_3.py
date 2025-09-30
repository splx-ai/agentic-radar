"""Minimal CrewAI crew demonstrating MCP tool integration.

Run prerequisites:
  - Ensure the MCP servers referenced below are running (or adjust/remove as needed).
  - Provide an `agents.yaml` and `tasks.yaml` (paths can be changed) containing at least
  entries for `your_agent` and `my_minimal_task`.
"""

import os
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task



@CrewBase
class CrewWithMCP:
  """Example crew with a single agent & task using MCP-provided tools."""

  # These can be changed to dicts loaded from YAML (like other examples) if desired.
  agents_config = {
    "your_agent": {
      "role": "Research Assistant",
      "goal": "Use available MCP tools to gather and summarize info",
      "backstory": "A focused assistant that leverages external tool servers.",
      "temperature": 0.2,
    }
  }

  tasks_config = {
    "my_minimal_task": {
      "description": "Collect a concise summary of the capabilities exposed by the MCP tools.",
      "expected_output": "A short markdown list summarizing each tool and one potential use case.",
    }
  }

  # Define MCP server connection parameters (adjust/remove as needed)
  mcp_server_params = [
    {  # Streamable HTTP Server
      "url": "http://localhost:8001/mcp",
      "transport": "streamable-http"
    },
    {  # SSE Server
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    },
    # StdIO Server example (only works if script exists)
    StdioServerParameters(
      command="python3",
      args=["servers/your_stdio_server.py"],
      env={"UV_PYTHON": "3.12", **os.environ},
    )
  ]

  def get_mcp_tools(self):  # Utility method used by the agent
    try:
      toolset = McpToolSet(self.mcp_server_params)
      return toolset.get_tools()  # returns list[BaseTool]
    except Exception:
      # If servers not available, proceed without tools (keeps example runnable)
      return []

  @agent
  def your_agent(self) -> Agent:
    return Agent(
      role="Research Assistant",
      goal="Use available MCP tools to gather and summarize info",
      backstory="A focused assistant that leverages external tool servers.",
      tools=self.get_mcp_tools(),  # all available MCP tools
      allow_delegation=False,
      verbose=True,
    )

  @task
  def my_minimal_task(self) -> Task:
    return Task(
      config=self.tasks_config["my_minimal_task"],
      agent=self.your_agent(),
    )

  @crew
  def crew(self) -> Crew:
    """Create the crew with a single agent and task."""
    return Crew(
      agents=self.agents,  # auto-collected by decorator
      tasks=self.tasks,    # auto-collected
      process=Process.sequential,
      verbose=True,
    )