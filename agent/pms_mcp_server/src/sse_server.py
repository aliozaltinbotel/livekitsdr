"""
SSE-based MCP Server for LiveKit compatibility
"""
import asyncio
import json
import uuid
import logging
from typing import Dict, Optional
from aiohttp import web
from aiohttp_sse import sse_response
from dotenv import load_dotenv
import os

from .api_client import PMSAPIClient
from .tools import PMSTools

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Global instances
sessions: Dict[str, asyncio.Queue] = {}
api_client: Optional[PMSAPIClient] = None
pms_tools: Optional[PMSTools] = None


async def health_check(request: web.Request) -> web.Response:
    """Health check endpoint"""
    return web.json_response({"status": "healthy", "service": "pms-mcp-sse-server"})


async def handle_sse(request: web.Request) -> web.Response:
    """Handle SSE connection for MCP protocol"""
    session_id = str(uuid.uuid4())
    message_queue = asyncio.Queue()
    sessions[session_id] = message_queue
    
    try:
        async with sse_response(request) as resp:
            # Send endpoint event first
            endpoint_url = f"/messages/?session_id={session_id}"
            await resp.send(endpoint_url, event="endpoint")
            
            # Process messages from queue
            while True:
                try:
                    message = await asyncio.wait_for(message_queue.get(), timeout=30.0)
                    if message is None:  # Shutdown signal
                        break
                    await resp.send(json.dumps(message), event="message")
                except asyncio.TimeoutError:
                    # Send keepalive
                    continue
                    
    finally:
        # Clean up session
        sessions.pop(session_id, None)
    
    return resp


async def handle_messages(request: web.Request) -> web.Response:
    """Handle POST messages from MCP client"""
    global pms_tools
    
    # Extract session ID
    session_id = request.query.get("session_id")
    if not session_id or session_id not in sessions:
        return web.json_response({"error": "Invalid session"}, status=400)
    
    message_queue = sessions[session_id]
    
    try:
        # Parse the message
        data = await request.json()
        message = data.get("message", {})
        method = message.get("method")
        params = message.get("params", {})
        request_id = message.get("id")
        
        # Process the request
        result = None
        error = None
        
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "pms-mcp-server",
                    "version": "1.0.0"
                }
            }
        
        elif method == "tools/list":
            if pms_tools:
                tools = pms_tools.get_available_tools()
                result = {"tools": [tool.model_dump() for tool in tools]}
            else:
                result = {"tools": []}
        
        elif method == "tools/call":
            if not pms_tools:
                error = {"code": -32603, "message": "Tools not initialized"}
            else:
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                try:
                    tool_result = await pms_tools.execute_tool(tool_name, arguments)
                    result = {"content": tool_result}
                except Exception as e:
                    error = {"code": -32603, "message": str(e)}
        
        else:
            error = {"code": -32601, "message": f"Method not found: {method}"}
        
        # Send response
        response = {
            "jsonrpc": "2.0",
            "id": request_id
        }
        
        if error:
            response["error"] = error
        else:
            response["result"] = result
        
        await message_queue.put(response)
        
        return web.Response(status=204)  # No content
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return web.json_response({"error": str(e)}, status=500)


async def init_app() -> web.Application:
    """Initialize the web application"""
    global api_client, pms_tools
    
    # Get configuration
    base_url = os.getenv("PMS_BASE_URL", "https://pms.botel.ai")
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
    app.router.add_get("/sse", handle_sse)
    app.router.add_post("/messages/", handle_messages)
    
    # Add CORS middleware
    async def cors_middleware(request, handler):
        response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
    
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
    
    logging.basicConfig(level=logging.INFO)
    logger.info(f"Starting PMS MCP SSE Server on port {port}")
    logger.info(f"SSE endpoint: http://localhost:{port}/sse")
    logger.info(f"Messages endpoint: http://localhost:{port}/messages/")
    
    app = init_app()
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()