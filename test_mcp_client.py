#!/usr/bin/env python3

"""
Test client for the iMessage Analysis MCP Server
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Tool arguments mapping
TOOL_ARGUMENTS = {
    "get_basic_statistics": {},
    "get_word_frequency": {"top_n": 10},
    "get_conversation_analysis": {"top_n": 5},
    "list_contacts": {"limit": 10},
    "search_messages": {"query": "hello", "limit": 5},
    "get_contact_statistics": {"contact": "+1 (630) 881-5887"},
    "get_conversation": {"contact": "+1 (630) 881-5887", "limit": 10}
}

async def test_mcp_server():
    """Test the iMessage Analysis MCP server"""
    
    # Server parameters for stdio connection
    server_params = StdioServerParameters(
        command="python3",
        args=["mcp_server.py"],
        env=None
    )
    
    print("🔌 Connecting to iMessage Analysis MCP Server...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("✅ Connected successfully!")
                
                # List available tools
                tools = await session.list_tools()
                print(f"\n📋 Available Tools ({len(tools.tools)}):")
                for tool in tools.tools:
                    print(f"  - {tool.name}")
                
                
                while True:
                    tool_name = input("Please enter the exact name of the tool you want to test: ")
                    result = await session.call_tool(tool_name, arguments={})
                    print(result.content[0].text if result.content else "No content")
                    if input("Do you want to test another tool? (y/n): ").lower() == "n":
                        break
                
                # Test all tools a
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Full Disk Access permission for Terminal/Python")
        print("2. MCP dependencies installed: pip install mcp[cli]")
        print("3. iMessage data accessible")

if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 