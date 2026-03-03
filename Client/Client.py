
import asyncio
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient


async def run_memory_chat():
    """
    Interactive MCP Chat with:
    - Groq LLM
    - MCP tools via config file
    - Built-in conversation memory
    """

    # Load environment variables
    load_dotenv()

    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY not found in environment variables")

    # MCP configuration file
    config_file = "config/mcp.json"

    print("🚀 Initializing MCP Chat...")

    # Create MCP client from config
    client = MCPClient.from_config_file(config_file)

    # Create Groq LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0
    )

    # Create MCP Agent
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True
    )

    print("\n===== 🧠 Interactive MCP Chat =====")
    print("Type 'exit' or 'quit' to end")
    print("Type 'clear' to reset conversation memory")
    print("====================================\n")

    try:
        while True:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("👋 Ending conversation...")
                break

            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("🧹 Conversation history cleared.")
                continue

            print("\nAssistant:", end=" ", flush=True)

            try:
                response = await agent.run(user_input)
                print(response)

            except Exception as e:
                print(f"\n❌ Error: {e}")

    finally:
        print("\n🔒 Closing MCP sessions...")
        if client and client.sessions:
            await client.close_all_sessions()
        print("✅ Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(run_memory_chat())