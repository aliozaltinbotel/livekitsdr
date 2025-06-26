#!/usr/bin/env python3
"""Test MCP server connection and PMS API tools"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_mcp_connection():
    """Test connection to MCP server and execute get_customer_properties_context tool"""
    
    # MCP server URL
    mcp_url = "http://localhost:3001"
    
    async with aiohttp.ClientSession() as session:
        # 1. Connect to SSE endpoint
        print("1. Connecting to SSE endpoint...")
        async with session.get(f"{mcp_url}/sse") as sse_response:
            if sse_response.status != 200:
                print(f"Failed to connect to SSE: {sse_response.status}")
                return
                
            # Read the endpoint URL from SSE
            async for line in sse_response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('event: endpoint'):
                    # Next line should have the data
                    continue
                if line.startswith('data: '):
                    endpoint_path = line[6:]  # Remove 'data: ' prefix
                    print(f"Got endpoint: {endpoint_path}")
                    break
            
            # 2. Send initialize request
            messages_url = f"{mcp_url}{endpoint_path}"
            print(f"\n2. Sending initialize request to {messages_url}")
            
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05"
                },
                "id": 1
            }
            
            async with session.post(messages_url, json=init_request) as resp:
                if resp.status != 204:
                    print(f"Initialize failed: {resp.status}")
                    return
            
            # Read response from SSE
            response = None
            async for line in sse_response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    try:
                        response = json.loads(line[6:])
                        print(f"Initialize response: {json.dumps(response, indent=2)}")
                        break
                    except:
                        continue
            
            # 3. List available tools
            print("\n3. Listing available tools...")
            list_tools_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
            
            async with session.post(messages_url, json=list_tools_request) as resp:
                if resp.status != 204:
                    print(f"List tools failed: {resp.status}")
                    return
            
            # Read response
            async for line in sse_response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    try:
                        response = json.loads(line[6:])
                        print(f"Available tools: {json.dumps(response, indent=2)}")
                        break
                    except:
                        continue
            
            # 4. Call get_customer_properties_context tool
            print("\n4. Calling get_customer_properties_context tool...")
            tool_call_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_customer_properties_context",
                    "arguments": {
                        "include_inactive": True
                    }
                },
                "id": 3
            }
            
            async with session.post(messages_url, json=tool_call_request) as resp:
                if resp.status != 204:
                    print(f"Tool call failed: {resp.status}")
                    return
            
            # Read response
            async for line in sse_response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    try:
                        response = json.loads(line[6:])
                        if 'result' in response and 'content' in response['result']:
                            content = response['result']['content']
                            if isinstance(content, list) and len(content) > 0:
                                print(f"\nProperty Context:\n{content[0]['text']}")
                        elif 'error' in response:
                            print(f"Error: {response['error']}")
                        break
                    except Exception as e:
                        print(f"Error parsing response: {e}")
                        continue

if __name__ == "__main__":
    print("Testing MCP Server Connection and PMS API Tools")
    print("=" * 50)
    asyncio.run(test_mcp_connection())