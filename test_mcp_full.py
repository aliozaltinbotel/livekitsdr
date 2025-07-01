#!/usr/bin/env python3
"""Full test of MCP server with SSE connection"""

import aiohttp
import asyncio
import json
from aiohttp_sse import EventSourceResponse

async def test_mcp_full():
    """Test the full MCP server flow"""
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Connect to SSE endpoint
        print("Connecting to SSE endpoint...")
        
        # We need to handle SSE in a separate task
        async def connect_sse():
            session_id = None
            message_queue = asyncio.Queue()
            
            async with session.get('http://localhost:3001/sse') as resp:
                async for msg in resp.content.iter_any():
                    data = msg.decode('utf-8')
                    lines = data.strip().split('\n')
                    
                    for line in lines:
                        if line.startswith('event: endpoint'):
                            continue
                        elif line.startswith('data: '):
                            content = line[6:]
                            if content.startswith('/messages/'):
                                # Extract session ID
                                session_id = content.split('session_id=')[1]
                                print(f"Got session ID: {session_id}")
                                return session_id, message_queue
                        elif line.startswith('event: message'):
                            continue
                        elif line.startswith('data: ') and session_id:
                            # This is a message response
                            try:
                                msg_data = json.loads(line[6:])
                                await message_queue.put(msg_data)
                            except json.JSONDecodeError:
                                pass
        
        # Connect and get session ID
        sse_task = asyncio.create_task(connect_sse())
        
        try:
            session_id, message_queue = await asyncio.wait_for(sse_task, timeout=5.0)
        except asyncio.TimeoutError:
            print("Failed to connect to SSE endpoint")
            return
        
        # Step 2: Initialize the session
        print("\nInitializing MCP session...")
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
        
        async with session.post(
            f'http://localhost:3001/messages/?session_id={session_id}', 
            json=init_msg
        ) as resp:
            if resp.status != 204:
                print(f"Initialize failed: {resp.status}")
                return
        
        # Step 3: Call the tool
        print("\nCalling get_customer_properties_context tool...")
        tool_call_msg = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_customer_properties_context",
                "arguments": {
                    "include_inactive": False
                }
            },
            "id": 2
        }
        
        async with session.post(
            f'http://localhost:3001/messages/?session_id={session_id}', 
            json=tool_call_msg
        ) as resp:
            if resp.status != 204:
                print(f"Tool call failed: {resp.status}")
                text = await resp.text()
                print(f"Error: {text}")
                return
        
        print("Tool call sent successfully!")

if __name__ == "__main__":
    asyncio.run(test_mcp_full())