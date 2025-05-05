from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o")

async def main():

    async with MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["/path/to/math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            }
        }
    ) as client:
        agent = create_react_agent(model, client.get_tools())
        math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
        weather_response = await agent.ainvoke({"messages": "what is the weather in nyc?"})

import asyncio
asyncio.run(main())