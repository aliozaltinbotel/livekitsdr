#!/usr/bin/env python3
"""Test script for PMS MCP Server"""

import asyncio
import aiohttp
import json
import uuid

async def test_mcp_server():
    """Test the MCP server SSE connection and tool calls"""
    
    # First, establish SSE connection
    session_id = None
    
    async with aiohttp.ClientSession() as session:
        # Connect to SSE endpoint
        print("Connecting to SSE endpoint...")
        async with session.get('http://localhost:3001/sse') as resp:
            async for data in resp.content:
                line = data.decode('utf-8').strip()
                if line.startswith('event: endpoint'):
                    # Next line contains the data
                    continue
                elif line.startswith('data: '):
                    endpoint_data = line[6:]  # Remove 'data: ' prefix
                    if endpoint_data.startswith('/messages/'):
                        # Extract session ID from endpoint URL
                        session_id = endpoint_data.split('session_id=')[1]
                        print(f"Got session ID: {session_id}")
                        break
        
        if not session_id:
            print("Failed to get session ID")
            return
        
        # Initialize the connection
        print("\nInitializing MCP connection...")
        init_msg = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    }
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        # Send initialize request
        async with session.post(f'http://localhost:3001/messages/?session_id={session_id}', 
                              json=init_msg) as resp:
            if resp.status != 204:
                print(f"Initialize failed: {resp.status}")
                return
        
        # Wait a bit for response
        await asyncio.sleep(0.5)
        
        # List available tools
        print("\nListing available tools...")
        list_tools_msg = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        async with session.post(f'http://localhost:3001/messages/?session_id={session_id}', 
                              json=list_tools_msg) as resp:
            if resp.status != 204:
                print(f"List tools failed: {resp.status}")
                return
        
        # Wait a bit
        await asyncio.sleep(0.5)
        
        # Call the get_customer_properties_context tool
        print("\nCalling get_customer_properties_context tool...")
        call_tool_msg = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_customer_properties_context",
                "arguments": {
                    "include_inactive": False
                }
            },
            "id": 3
        }
        
        async with session.post(f'http://localhost:3001/messages/?session_id={session_id}', 
                              json=call_tool_msg) as resp:
            if resp.status != 204:
                print(f"Tool call failed: {resp.status}")
                text = await resp.text()
                print(f"Error: {text}")
                return
        
        print("\nTool call sent successfully!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())