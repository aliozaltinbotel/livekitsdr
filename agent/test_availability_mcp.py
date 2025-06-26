#!/usr/bin/env python3
"""Test the new availability and pricing MCP tool"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

async def test_availability_mcp_tool():
    """Test the availability and pricing check MCP tool"""
    
    print("Testing MCP Availability & Pricing Tool")
    print("=" * 80)
    
    mcp_url = "http://localhost:3001"
    
    async with aiohttp.ClientSession() as session:
        # Connect to SSE
        async with session.get(f"{mcp_url}/sse") as sse_response:
            if sse_response.status != 200:
                print(f"Failed to connect to SSE: {sse_response.status}")
                return
                
            # Read the endpoint URL
            async for line in sse_response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    endpoint_path = line[6:]
                    break
            
            messages_url = f"{mcp_url}{endpoint_path}"
            
            # Initialize
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05"},
                "id": 1
            }
            
            await session.post(messages_url, json=init_request)
            
            # Skip init response
            async for line in sse_response.content:
                if line.decode('utf-8').startswith('data: '):
                    break
            
            # List available tools
            list_tools_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 2
            }
            
            await session.post(messages_url, json=list_tools_request)
            
            # Read tools list response
            async for line in sse_response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    try:
                        response = json.loads(line[6:])
                        if 'result' in response and 'tools' in response['result']:
                            print("Available MCP Tools:")
                            for tool in response['result']['tools']:
                                print(f"- {tool['name']}: {tool['description']}")
                            print()
                        break
                    except:
                        continue
            
            # Test 1: Check availability for next week
            print("\nTest 1: Check availability for next week (4 guests, no pets)")
            print("-" * 60)
            
            start_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            
            test1_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "check_property_availability_and_pricing",
                    "arguments": {
                        "property_id": "fde09fba-3a96-4705-a0c4-4bd264fb61da",
                        "check_in_date": start_date,
                        "check_out_date": end_date,
                        "guest_count": 4,
                        "include_pets": False
                    }
                },
                "id": 3
            }
            
            await session.post(messages_url, json=test1_request)
            
            # Read response
            async for line in sse_response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    try:
                        response = json.loads(line[6:])
                        if 'result' in response and 'content' in response['result']:
                            content = response['result']['content']
                            if isinstance(content, list) and len(content) > 0:
                                print(content[0]['text'])
                        break
                    except:
                        continue
            
            # Test 2: Check with pets
            print("\n\nTest 2: Check same dates with pets included")
            print("-" * 60)
            
            test2_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "check_property_availability_and_pricing",
                    "arguments": {
                        "property_id": "fde09fba-3a96-4705-a0c4-4bd264fb61da",
                        "check_in_date": start_date,
                        "check_out_date": end_date,
                        "guest_count": 4,
                        "include_pets": True
                    }
                },
                "id": 4
            }
            
            await session.post(messages_url, json=test2_request)
            
            # Read response
            async for line in sse_response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    try:
                        response = json.loads(line[6:])
                        if 'result' in response and 'content' in response['result']:
                            content = response['result']['content']
                            if isinstance(content, list) and len(content) > 0:
                                print(content[0]['text'])
                        break
                    except:
                        continue
            
            # Test 3: Check with too many guests
            print("\n\nTest 3: Check with too many guests (10 guests)")
            print("-" * 60)
            
            test3_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "check_property_availability_and_pricing",
                    "arguments": {
                        "property_id": "fde09fba-3a96-4705-a0c4-4bd264fb61da",
                        "check_in_date": start_date,
                        "check_out_date": end_date,
                        "guest_count": 10,
                        "include_pets": False
                    }
                },
                "id": 5
            }
            
            await session.post(messages_url, json=test3_request)
            
            # Read response
            async for line in sse_response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    try:
                        response = json.loads(line[6:])
                        if 'result' in response and 'content' in response['result']:
                            content = response['result']['content']
                            if isinstance(content, list) and len(content) > 0:
                                print(content[0]['text'])
                        break
                    except:
                        continue

if __name__ == "__main__":
    # Load PMS server env
    load_dotenv('/Users/aliozaltin/Desktop/livekitsdr/agent/pms_mcp_server/.env')
    
    asyncio.run(test_availability_mcp_tool())