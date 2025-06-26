#!/usr/bin/env python3
"""Test MCP server with updated tools to see all property fields"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

async def test_all_property_fields():
    """Test to verify all property fields are being returned"""
    
    print("Testing MCP Tool with All Property Fields")
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
            
            # Call tool
            tool_call_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_customer_properties_context",
                    "arguments": {"include_inactive": False}
                },
                "id": 2
            }
            
            await session.post(messages_url, json=tool_call_request)
            
            # Read response
            async for line in sse_response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    try:
                        response = json.loads(line[6:])
                        if 'result' in response and 'content' in response['result']:
                            content = response['result']['content']
                            if isinstance(content, list) and len(content) > 0:
                                text = content[0]['text']
                                
                                print("MCP Tool Response - All Property Fields:")
                                print("-" * 80)
                                print(text)
                                print("-" * 80)
                                
                                # Check for all expected fields
                                expected_fields = [
                                    "Location", "Max Occupancy", "Bedrooms", "Bathrooms", 
                                    "Check-in Time", "Check-out Time", "WiFi Network", 
                                    "WiFi Password", "Door Code", "Property Manager",
                                    "Base Price", "Cleaning Fee", "Amenities", "Description",
                                    "Time Zone", "Images Available"
                                ]
                                
                                print("\nField Verification:")
                                for field in expected_fields:
                                    if field in text:
                                        print(f"✅ {field} - FOUND")
                                    else:
                                        print(f"❌ {field} - MISSING")
                                
                        break
                    except Exception as e:
                        print(f"Error parsing response: {e}")
                        continue

if __name__ == "__main__":
    # Load PMS server env
    load_dotenv('/Users/aliozaltin/Desktop/livekitsdr/agent/pms_mcp_server/.env')
    
    asyncio.run(test_all_property_fields())