from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP
import asyncio

server = MCPServerHTTP(url='http://192.168.1.40:8111/sse')  
agent = Agent('openai:gpt-4o', mcp_servers=[server])  

async def main():
    async with agent.run_mcp_servers():
        tools = await server.list_tools()
        print(tools)
        result = await agent.run('Please add the numbers 14 and 33')
    print(result.output)

if __name__ == "__main__":
    asyncio.run(main())