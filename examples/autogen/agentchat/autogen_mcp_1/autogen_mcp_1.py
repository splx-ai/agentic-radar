import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import SseMcpToolAdapter, SseServerParams
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken


async def main() -> None:
    # Create server params for the remote MCP service
    server_params = SseServerParams(
        url="https://api.example.com/mcp",
        headers={"Authorization": "Bearer your-api-key", "Content-Type": "application/json"},
        timeout=30,  # Connection timeout in seconds
    )

    # Get the translation tool from the server
    adapter = await SseMcpToolAdapter.from_server_params(server_params, "translate")

    # Create an agent that can use the translation tool
    model_client = OpenAIChatCompletionClient(model="gpt-4")
    agent = AssistantAgent(
        name="translator",
        model_client=model_client,
        tools=[adapter],
        system_message="You are a helpful translation assistant.",
    )

    # Let the agent translate some text
    await Console(
        agent.run_stream(task="Translate 'Hello, how are you?' to Spanish", cancellation_token=CancellationToken())
    )


if __name__ == "__main__":
    asyncio.run(main())