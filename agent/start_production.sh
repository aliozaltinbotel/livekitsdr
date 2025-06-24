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

# Start MCP server in background
echo "Starting MCP server..."
cd /app/pms_mcp_server
python -m src.sse_server &
MCP_PID=$!

# Wait for MCP server to be ready
echo "Waiting for MCP server to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:3001/health >/dev/null 2>&1; then
        echo "MCP server is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "ERROR: MCP server failed to start"
        exit 1
    fi
    sleep 1
done

# Update MCP server URL to use localhost
export PMS_MCP_SERVER_URL="http://localhost:3001/sse"

# Start agent
echo "Starting LiveKit agent..."
cd /app
python agent.py &
AGENT_PID=$!

# Log both PIDs
echo "MCP Server PID: $MCP_PID"
echo "Agent PID: $AGENT_PID"

# Wait for both processes
wait $MCP_PID $AGENT_PID