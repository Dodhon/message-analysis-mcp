#!/usr/bin/env python3

"""
Test client for the iMessage Analysis MCP Server
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

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
                    print(f"  • {tool.name}: {tool.description}")
                
                # Test basic statistics tool
                print("\n🔍 Testing basic statistics tool...")
                result = await session.call_tool("get_basic_statistics", arguments={})
                print("Basic Statistics Result:")
                print(result.content[0].text if result.content else "No content")
                
                # Test word frequency tool
                print("\n🔍 Testing word frequency tool...")
                result = await session.call_tool("get_word_frequency", arguments={"top_n": 5})
                print("Word Frequency Result:")
                print(result.content[0].text if result.content else "No content")
                
                # Test conversation analysis tool
                print("\n🔍 Testing conversation analysis tool...")
                result = await session.call_tool("get_conversation_analysis", arguments={"top_n": 3})
                print("Conversation Analysis Result:")
                print(result.content[0].text if result.content else "No content")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Full Disk Access permission for Terminal/Python")
        print("2. MCP dependencies installed: pip install mcp[cli]")
        print("3. iMessage data accessible")

if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 