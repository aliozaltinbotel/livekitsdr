#!/usr/bin/env python3
"""Direct test of MCP server tool call"""

import aiohttp
import asyncio
import json
import uuid

async def test_mcp_tool():
    """Test the MCP server tool call directly"""
    
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    
    async with aiohttp.ClientSession() as session:
        # Send the tool call request
        print("Testing MCP server tool call...")
        tool_call_msg = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_customer_properties_context",
                "arguments": {
                    "include_inactive": False
                }
            },
            "id": 1
        }
        
        # Create a queue to simulate SSE session
        print(f"Session ID: {session_id}")
        
        # Send the request
        async with session.post(
            f'http://localhost:3001/messages/?session_id={session_id}', 
            json=tool_call_msg
        ) as resp:
            print(f"Response status: {resp.status}")
            if resp.status != 204:
                text = await resp.text()
                print(f"Response text: {text}")

if __name__ == "__main__":
    asyncio.run(test_mcp_tool())