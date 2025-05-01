"""Example client that uses Pydantic AI to query an LLM using an MCP server"""

import asyncio
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP

server = MCPServerHTTP(url="http://192.168.1.40:3300/sse")
agent = Agent("openai:gpt-4o", mcp_servers=[server])


async def main():
    """
    Main function that uses an agent configured with an MCP server and sends a query
    """
    async with agent.run_mcp_servers():
        # Use the lines below if you want to see all the tools available from the MCP server
        tools = await server.list_tools()
        print(tools)
        result = await agent.run(
            "Are there any defibrillators within 300 metres of 9 Sugar Island, Newry"
        )
    print(result.output)


if __name__ == "__main__":
    asyncio.run(main())
