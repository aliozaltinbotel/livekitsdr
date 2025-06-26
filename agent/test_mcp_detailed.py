#!/usr/bin/env python3
"""Test MCP server to see detailed property data"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_detailed_property_data():
    """Test to see all property data fields"""
    
    # Direct API test first to see raw data
    print("1. Testing Direct API Call to see raw data structure")
    print("=" * 60)
    
    api_key = os.getenv("PMS_API_KEY")
    customer_id = os.getenv("PMS_CUSTOMER_ID", "ae0c85c5-7fa7-4e09-8a94-0df5da38e72e")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "customerId": customer_id,
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Get all properties
        async with session.get(
            "https://pms.botel.ai/api/Property/GetAll",
            headers=headers,
            params={"PageSize": 100}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print("GetAll Response:")
                print(json.dumps(data, indent=2))
                
                # Get first property ID for detailed lookup
                if data.get("items") and len(data["items"]) > 0:
                    property_id = data["items"][0]["id"]
                    print(f"\n\nGetting details for property ID: {property_id}")
                    print("=" * 60)
                    
                    # Get detailed property info
                    async with session.get(
                        "https://pms.botel.ai/api/Property/Get",
                        headers=headers,
                        params={"Id": property_id}
                    ) as detail_resp:
                        if detail_resp.status == 200:
                            detail_data = await detail_resp.json()
                            print("Detailed Property Response:")
                            print(json.dumps(detail_data, indent=2))
        
        print("\n\n2. Testing MCP Tool Response")
        print("=" * 60)
        
        # Now test via MCP to see what's included
        mcp_url = "http://localhost:3001"
        
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
            
            # Skip reading init response to save time
            async for line in sse_response.content:
                if line.decode('utf-8').startswith('data: '):
                    break
            
            # Call tool with include_inactive=True to see all properties
            tool_call_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_customer_properties_context",
                    "arguments": {
                        "include_inactive": True
                    }
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
                                print("MCP Tool Response (formatted context):")
                                print(content[0]['text'])
                        break
                    except:
                        continue

if __name__ == "__main__":
    # Load PMS server env file
    from dotenv import load_dotenv
    load_dotenv('/Users/aliozaltin/Desktop/livekitsdr/agent/pms_mcp_server/.env')
    
    print("Detailed Property Data Test")
    print("=" * 80)
    asyncio.run(test_detailed_property_data())