#!/bin/bash
# Start script for running MCP server and agent in the same container

set -e

# Function to handle shutdown
shutdown() {
    echo "Shutting down services..."
    kill $MCP_PID $AGENT_PID 2>/dev/null || true
    exit 0
}

# Trap signals for graceful shutdown
trap shutdown SIGTERM SIGINT

# Check if MCP server directory exists
if [ ! -d "/app/pms_mcp_server" ]; then
    echo "ERROR: MCP server directory not found at /app/pms_mcp_server"
    exit 1
fi

# Start MCP server in background with proper logging
echo "Starting MCP server..."
cd /app/pms_mcp_server
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Starting MCP server with command: python -m src.sse_server"

# Redirect MCP server output to ensure we see logs
python -m src.sse_server 2>&1 | while IFS= read -r line; do
    echo "[MCP Server] $line"
done &
MCP_PID=$!

# Give MCP server time to start
sleep 2

# Check if MCP process is still running
if ! kill -0 $MCP_PID 2>/dev/null; then
    echo "ERROR: MCP server process died immediately after starting"
    exit 1
fi

# Wait for MCP server to be ready
echo "Waiting for MCP server to be ready..."
for i in {1..30}; do
    echo "Checking MCP server health (attempt $i/30)..."
    if curl -f http://localhost:3001/health >/dev/null 2>&1; then
        echo "MCP server is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "ERROR: MCP server failed to start after 30 attempts"
        echo "Checking if process is still running..."
        if kill -0 $MCP_PID 2>/dev/null; then
            echo "MCP process is running but not responding on port 3001"
        else
            echo "MCP process has died"
        fi
        exit 1
    fi
    sleep 1
done

# Update MCP server URL to use localhost
export PMS_MCP_SERVER_URL="http://localhost:3001/sse"

# Start agent in production mode
echo "Starting LiveKit agent..."
cd /app
python agent.py start &
AGENT_PID=$!

# Log both PIDs
echo "MCP Server PID: $MCP_PID"
echo "Agent PID: $AGENT_PID"

# Wait for both processes
wait $MCP_PID $AGENT_PID