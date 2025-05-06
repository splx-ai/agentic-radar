from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from langchain_openai import ChatOpenAI

async def main():
    async with MultiServerMCPClient() as client:
        await client.connect_to_server(
            "math",
            command="python",
            args=["math_server.py"],
        )
        await client.connect_to_server(
            "weather",
            command="python",
            args=["weather_server.py"],
        )

    agent = create_react_agent(model, client.get_tools())
    math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})

import asyncio
asyncio.run(main())