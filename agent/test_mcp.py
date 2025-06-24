#!/usr/bin/env python3
"""
Test script to verify MCP server integration
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

async def test_mcp_connection():
    """Test MCP server connection and tool availability"""
    print("Testing MCP Server Connection...")
    print(f"MCP Server URL: {os.getenv('PMS_MCP_SERVER_URL', 'Not set')}")
    print(f"MCP Server Token: {'Set' if os.getenv('PMS_MCP_SERVER_TOKEN') else 'Not set'}")
    
    # Import after loading env vars
    from pms_mcp_tools import test_mcp_connection, get_customer_properties_context
    
    # Test connection
    connected = await test_mcp_connection()
    print(f"\nConnection test: {'✓ Passed' if connected else '✗ Failed'}")
    
    if connected:
        print("\nTesting get_customer_properties_context tool...")
        try:
            result = await get_customer_properties_context(include_inactive=False)
            print(f"Tool response preview (first 500 chars):\n{result[:500]}...")
        except Exception as e:
            print(f"Tool test failed: {e}")
    
    return connected

async def test_livekit_agent():
    """Test LiveKit agent with MCP integration"""
    print("\n\nTesting LiveKit Agent MCP Integration...")
    
    try:
        from agent import Assistant
        
        # Create assistant instance
        assistant = Assistant()
        print("✓ Assistant created successfully")
        
        # Check MCP servers
        if hasattr(assistant, '_mcp_servers'):
            print(f"✓ MCP servers configured: {len(assistant._mcp_servers)} server(s)")
        else:
            print("✗ No MCP servers found")
        
        # Check available tools
        if hasattr(assistant, '_tools'):
            print(f"✓ Direct tools configured: {len(assistant._tools)} tool(s)")
            for tool in assistant._tools:
                print(f"  - {tool.__name__ if hasattr(tool, '__name__') else tool}")
        
        return True
        
    except Exception as e:
        print(f"✗ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("MCP Integration Test Suite")
    print("=" * 60)
    
    # Test 1: MCP Connection
    mcp_ok = await test_mcp_connection()
    
    # Test 2: LiveKit Agent
    agent_ok = await test_livekit_agent()
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"- MCP Connection: {'✓ Passed' if mcp_ok else '✗ Failed'}")
    print(f"- Agent Integration: {'✓ Passed' if agent_ok else '✗ Failed'}")
    print("=" * 60)
    
    return mcp_ok and agent_ok

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)