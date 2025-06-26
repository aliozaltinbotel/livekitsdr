#!/usr/bin/env python3
"""Check system status and MCP data structure"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_system_status():
    """Check complete system status"""
    
    print("=" * 80)
    print("SYSTEM STATUS CHECK")
    print(f"Time: {datetime.now()}")
    print("=" * 80)
    
    # 1. Check MCP Server Status
    print("\n1. MCP SERVER STATUS")
    print("-" * 40)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check health endpoint
            async with session.get("http://localhost:3001/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ MCP Server is healthy: {data}")
                else:
                    print(f"❌ MCP Server health check failed: {resp.status}")
    except Exception as e:
        print(f"❌ MCP Server not running: {e}")
    
    # 2. Check Environment Variables
    print("\n2. ENVIRONMENT VARIABLES")
    print("-" * 40)
    
    required_vars = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY",
        "ASSEMBLYAI_API_KEY",
        "CARTESIA_API_KEY",
        "PMS_API_KEY",
        "PMS_CUSTOMER_ID"
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show first 10 chars for security
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")
    
    # 3. Test MCP Data Structure
    print("\n3. MCP DATA STRUCTURE TEST")
    print("-" * 40)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Connect to SSE
            async with session.get("http://localhost:3001/sse") as sse_response:
                if sse_response.status != 200:
                    print(f"❌ Failed to connect to SSE: {sse_response.status}")
                    return
                
                # Get endpoint
                endpoint_path = None
                async for line in sse_response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        endpoint_path = line[6:]
                        break
                
                if not endpoint_path:
                    print("❌ Failed to get endpoint path")
                    return
                
                messages_url = f"http://localhost:3001{endpoint_path}"
                
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
                
                # Call get_customer_properties_context
                tool_call_request = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "get_customer_properties_context",
                        "arguments": {"include_inactive": True}
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
                                    
                                    print("✅ MCP Tool Response Structure:")
                                    print(f"   - Response type: {type(response)}")
                                    print(f"   - Content type: {type(content)}")
                                    print(f"   - Content length: {len(content)}")
                                    print(f"   - Text type: {type(text)}")
                                    print(f"   - Text length: {len(text)} characters")
                                    
                                    # Parse the text to show data structure
                                    print("\n   Parsed Data Fields:")
                                    lines = text.split('\n')
                                    for line in lines:
                                        if line.startswith('- **'):
                                            field = line.split('**')[1]
                                            print(f"     • {field}")
                                    
                                    # Show property count
                                    if "Total Properties:" in text:
                                        for line in lines:
                                            if "Total Properties:" in line:
                                                print(f"\n   {line.strip()}")
                                            elif "Active Properties:" in line:
                                                print(f"   {line.strip()}")
                                                
                            elif 'error' in response:
                                print(f"❌ MCP Error: {response['error']}")
                            break
                        except Exception as e:
                            print(f"❌ Error parsing response: {e}")
                            continue
                            
    except Exception as e:
        print(f"❌ MCP test failed: {e}")
    
    # 4. Check Recent Logs
    print("\n4. RECENT LOG ANALYSIS")
    print("-" * 40)
    
    # Check agent log for errors
    if os.path.exists("agent.log"):
        with open("agent.log", "r") as f:
            lines = f.readlines()
            error_count = sum(1 for line in lines if "ERROR" in line)
            warning_count = sum(1 for line in lines if "WARNING" in line)
            
            print(f"Agent Log:")
            print(f"  - Total lines: {len(lines)}")
            print(f"  - Errors: {error_count}")
            print(f"  - Warnings: {warning_count}")
            
            if error_count > 0:
                print("\n  Recent errors:")
                error_lines = [line for line in lines if "ERROR" in line]
                for line in error_lines[-3:]:  # Last 3 errors
                    print(f"    {line.strip()}")
    
    # Check MCP server log
    if os.path.exists("pms_mcp_server/mcp_server_new.log"):
        with open("pms_mcp_server/mcp_server_new.log", "r") as f:
            lines = f.readlines()
            success_count = sum(1 for line in lines if "200 OK" in line)
            error_count = sum(1 for line in lines if "ERROR" in line or "401" in line or "404" in line)
            
            print(f"\nMCP Server Log:")
            print(f"  - Total lines: {len(lines)}")
            print(f"  - Successful API calls: {success_count}")
            print(f"  - Failed API calls: {error_count}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    # Load PMS server env
    load_dotenv('/Users/aliozaltin/Desktop/livekitsdr/agent/pms_mcp_server/.env')
    
    asyncio.run(check_system_status())