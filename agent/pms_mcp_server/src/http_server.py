"""
HTTP Server for PMS MCP
Provides an HTTP interface for the MCP server
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional
from aiohttp import web
from dotenv import load_dotenv

from .api_client import PMSAPIClient
from .tools import PMSTools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
api_client: Optional[PMSAPIClient] = None
pms_tools: Optional[PMSTools] = None


async def health_check(request: web.Request) -> web.Response:
    """Health check endpoint"""
    return web.json_response({"status": "healthy", "service": "pms-mcp-server"})


async def list_tools(request: web.Request) -> web.Response:
    """List all available tools"""
    global pms_tools
    
    if not pms_tools:
        return web.json_response({"error": "Tools not initialized"}, status=500)
    
    tools = pms_tools.get_available_tools()
    return web.json_response({
        "jsonrpc": "2.0",
        "result": {
            "tools": [tool.dict() for tool in tools]
        },
        "id": 1
    })


async def handle_rpc(request: web.Request) -> web.Response:
    """Handle JSON-RPC requests"""
    global pms_tools
    
    try:
        # Parse request - handle both GET and POST
        if request.method == "POST":
            data = await request.json()
        else:
            # For GET requests, parse query parameters
            data = {
                "method": request.query.get("method", ""),
                "params": json.loads(request.query.get("params", "{}")),
                "id": request.query.get("id", 1)
            }
        
        method = data.get("method")
        params = data.get("params", {})
        request_id = data.get("id", 1)
        
        # Check authorization if token is set
        auth_token = os.getenv("MCP_AUTH_TOKEN")
        if auth_token:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer ") or auth_header[7:] != auth_token:
                return web.json_response({
                    "jsonrpc": "2.0",
                    "error": {"code": -32001, "message": "Unauthorized"},
                    "id": request_id
                }, status=401)
        
        # Route methods
        if method == "tools/list":
            tools = pms_tools.get_available_tools()
            result = {"tools": [tool.dict() for tool in tools]}
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not tool_name:
                return web.json_response({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Tool name required"},
                    "id": request_id
                }, status=400)
            
            # Execute tool
            result = await pms_tools.execute_tool(tool_name, arguments)
            # Convert TextContent to dict
            result = {"content": [{"type": item.type, "text": item.text} for item in result]}
        
        else:
            return web.json_response({
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method not found: {method}"},
                "id": request_id
            }, status=404)
        
        # Return success response
        return web.json_response({
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        })
        
    except json.JSONDecodeError:
        return web.json_response({
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None
        }, status=400)
    
    except Exception as e:
        logger.error(f"Error handling RPC request: {e}")
        return web.json_response({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            "id": request_id
        }, status=500)


async def init_app() -> web.Application:
    """Initialize the web application"""
    global api_client, pms_tools
    
    # Get configuration
    base_url = os.getenv("PMS_BASE_URL", os.getenv("PMS_API_URL", "https://pms.botel.ai"))
    api_key = os.getenv("PMS_API_KEY")
    
    if not api_key:
        logger.warning("PMS_API_KEY not set in environment variables")
    
    # Initialize API client and tools
    api_client = PMSAPIClient(base_url=base_url, api_key=api_key)
    pms_tools = PMSTools(api_client)
    
    # Create app
    app = web.Application()
    
    # Add routes
    app.router.add_get("/health", health_check)
    app.router.add_get("/tools", list_tools)
    app.router.add_post("/rpc", handle_rpc)
    app.router.add_get("/rpc", handle_rpc)  # Support GET for SSE transport
    
    # Add CORS middleware
    async def cors_middleware(app, handler):
        async def middleware_handler(request):
            response = await handler(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response
        return middleware_handler
    
    app.middlewares.append(cors_middleware)
    
    # Cleanup on shutdown
    async def cleanup(app):
        if api_client:
            await api_client.close()
    
    app.on_cleanup.append(cleanup)
    
    return app


def main():
    """Main entry point"""
    port = int(os.getenv("PORT", "3001"))
    
    logger.info(f"Starting PMS MCP HTTP Server on port {port}")
    logger.info(f"Health check: http://localhost:{port}/health")
    logger.info(f"RPC endpoint: http://localhost:{port}/rpc")
    
    app = init_app()
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()