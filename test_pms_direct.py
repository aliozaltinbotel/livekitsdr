#!/usr/bin/env python3
"""Direct test of PMS API client and tools"""

import asyncio
import sys
import os

# Add the MCP server src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent', 'pms_mcp_server'))

from src.api_client import PMSAPIClient
from src.tools import PMSTools

async def test_pms_tools():
    """Test PMS tools directly"""
    
    # Initialize API client
    api_client = PMSAPIClient()
    tools = PMSTools(api_client)
    
    try:
        print("Testing get_customer_properties_context tool...")
        result = await tools.execute_tool(
            "get_customer_properties_context",
            {"include_inactive": False}
        )
        
        print("\nResult:")
        for content in result:
            print(content.text)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await api_client.close()

if __name__ == "__main__":
    asyncio.run(test_pms_tools())