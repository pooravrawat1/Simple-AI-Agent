from mcp import ClientSession, StudioServerParameters
from mcp.client.studio import studio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import aysyncio
import os

load_dotenv()

model = ChatOpenAI(model="gpt-4", 
                   temperature=0,
                   openai_api_key=os.getenv("OPENAI_API_KEY"))

server_params = StudioServerParameters(
    command = "npx",
    env = {
        "FIRECRAWL_API_KEY" : os.getenv("FIRECRAWL_API_KEY"),
    },
    args = ["firecrawl-mcp"]
)

async def main():
    async with studio_client(server_params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools, verbose = True)
            messages = [
                {
                "role": "user",
                "content": "Can you help me find information about the latest advancements in AI?"
                }
            ]

            print("Available tools:")
            for tool in tools:
                print(f"- {tool.name}")
            print("-" * 60)

            while True:
                user_input = input("YOU >")
                if user_input.lower() in ["exit", "quit"]:
                    print("Exiting the chat. Goodbye!")
                    break
                messages.append({"role": "user", "content": user_input[:175000]})

                try:
                    agent_response = await agent.ainvoke({"messages": messages})
                    ai_message = agent_response['messages'][-1].content
                    print("\nAI >", ai_message)
                except Exception as e:
                    print(f"Error: {e}")
                    
    if __name__ == "__main__":
        asyncio.run(main())

        
