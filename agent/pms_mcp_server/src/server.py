import asyncio
import os
from typing import Any, Optional
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from dotenv import load_dotenv

from .api_client import PMSAPIClient
from .tools import PMSTools

# Load environment variables
load_dotenv()

# Initialize the MCP server
server = Server("pms-mcp-server")

# Global instances
api_client = None
pms_tools = None

@server.list_tools()
async def handle_list_tools():
    """List all available PMS tools"""
    global pms_tools
    if not pms_tools:
        return []
    return pms_tools.get_available_tools()

@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[dict] = None) -> list:
    """Execute a PMS tool"""
    global pms_tools
    
    if not pms_tools:
        raise RuntimeError("PMS tools not initialized")
    
    return await pms_tools.execute_tool(name, arguments or {})

async def main():
    global api_client, pms_tools
    
    # Get API configuration from environment
    base_url = os.getenv("PMS_BASE_URL", "https://pms.botel.ai")
    api_key = os.getenv("PMS_API_KEY")
    
    if not api_key:
        print("Warning: PMS_API_KEY not set in environment variables")
        print("Please set it using: export PMS_API_KEY=your-api-key")
    
    # Initialize API client and tools
    api_client = PMSAPIClient(base_url=base_url, api_key=api_key)
    pms_tools = PMSTools(api_client)
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pms-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
    
    # Cleanup
    if api_client:
        await api_client.close()

if __name__ == "__main__":
    asyncio.run(main())