"""
PMS MCP Tools Integration for LiveKit Voice Agent

This module provides integration with the PMS MCP server to fetch
customer property context for the voice agent.
"""

import os
import logging
import asyncio
import json
from typing import Dict, Any, Optional, List
from livekit.agents import llm
import aiohttp

logger = logging.getLogger(__name__)

# MCP Server configuration
MCP_SERVER_URL = os.getenv("PMS_MCP_SERVER_URL", "http://localhost:3001")
MCP_SERVER_TOKEN = os.getenv("PMS_MCP_SERVER_TOKEN", "")

# PMS API configuration (if needed for direct calls)
PMS_API_URL = os.getenv("PMS_API_URL", "https://api-dev.botel.ai")
PMS_API_KEY = os.getenv("PMS_API_KEY", "")


class PMSMCPClient:
    """Client for interacting with the PMS MCP server"""
    
    def __init__(self, server_url: str = MCP_SERVER_URL, token: str = MCP_SERVER_TOKEN):
        self.server_url = server_url.rstrip('/')
        self.token = token
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            "Content-Type": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }
        
        try:
            async with self.session.post(
                f"{self.server_url}/rpc",
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"MCP server error: {response.status} - {text}")
                    return {"error": f"Server error: {response.status}"}
                
                result = await response.json()
                if "error" in result:
                    logger.error(f"MCP RPC error: {result['error']}")
                    return {"error": result["error"]}
                
                return result.get("result", {})
        except Exception as e:
            logger.error(f"Error calling MCP tool: {e}")
            return {"error": str(e)}


# Create the LiveKit tool function
@llm.ai_callable(
    description="""Get comprehensive context about all properties belonging to the current customer.
    This tool fetches property information from the PMS system to provide context for conversations.
    
    Use this tool when:
    - The customer asks about their properties
    - You need to understand what properties the customer owns/manages
    - You need property details like location, capacity, status, etc.
    
    The tool will return a formatted context document with:
    - Total number of properties
    - Active vs inactive property count
    - Detailed information for each property (name, location, capacity, type, etc.)
    """
)
async def get_customer_properties_context(
    include_inactive: bool = False
) -> str:
    """
    Fetch all properties for the customer and their detailed information.
    
    Args:
        include_inactive: Whether to include inactive properties (default: False)
    
    Returns:
        A formatted string containing comprehensive property context
    """
    try:
        # Try to use MCP server first
        async with PMSMCPClient() as client:
            result = await client.call_tool(
                "get_customer_properties_context",
                {"include_inactive": include_inactive}
            )
            
            if "error" in result:
                return f"Error fetching property context: {result['error']}"
            
            # Extract the text content from the result
            if isinstance(result, dict) and "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    return content[0].get("text", "No property information available")
            
            return str(result)
            
    except Exception as e:
        logger.error(f"Error in get_customer_properties_context: {e}")
        return f"I apologize, but I couldn't fetch your property information at this moment. Error: {str(e)}"


# Alternative direct API implementation (fallback)
async def get_customer_properties_direct(
    customer_id: str,
    include_inactive: bool = False
) -> str:
    """
    Direct API call to PMS system (fallback if MCP server is unavailable)
    """
    try:
        headers = {
            "x-api-key": PMS_API_KEY,
            "x-customer-id": customer_id,
            "Content-Type": "application/json"
        }
        
        params = {
            "PageSize": 100,
            "Status": None if include_inactive else True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{PMS_API_URL}/api/Property/GetAll",
                headers=headers,
                params=params
            ) as response:
                if response.status != 200:
                    return f"Error fetching properties: HTTP {response.status}"
                
                data = await response.json()
                properties = data.get("items", [])
                total_count = data.get("totalCount", 0)
                
                # Format the response
                context_parts = [
                    f"# Customer Property Context\n",
                    f"Total Properties: {total_count}\n",
                    f"Active Properties: {len([p for p in properties if p.get('status', False)])}\n\n"
                ]
                
                for idx, prop in enumerate(properties, 1):
                    context_parts.append(f"## Property {idx}: {prop.get('name', 'Unknown')}\n")
                    context_parts.append(f"- Status: {'Active' if prop.get('status', False) else 'Inactive'}\n")
                    context_parts.append(f"- ID: {prop.get('id')}\n\n")
                
                return "".join(context_parts)
                
    except Exception as e:
        logger.error(f"Error in direct API call: {e}")
        return f"Error fetching property information: {str(e)}"


# Function to test the MCP connection
async def test_mcp_connection():
    """Test if the MCP server is accessible"""
    try:
        async with PMSMCPClient() as client:
            # Try to call the tool with a simple request
            result = await client.call_tool(
                "get_customer_properties_context",
                {"include_inactive": False}
            )
            return "error" not in result
    except:
        return False


# Export the tool for use in the agent
pms_property_context_tool = get_customer_properties_context