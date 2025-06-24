#!/bin/bash

# Build and deploy Python agent to Azure with MCP server check

set -e  # Exit on error

echo "================================================"
echo "Deploying LiveKit Agent to Azure"
echo "================================================"

# Function to check if MCP server is running
check_mcp_server() {
    echo "Checking MCP server status..."
    
    # Check if running as systemd service
    if systemctl is-active --quiet pms-mcp-server 2>/dev/null; then
        echo "✓ MCP server is running as systemd service"
        return 0
    fi
    
    # Check if running on port 3001
    if lsof -i:3001 > /dev/null 2>&1; then
        echo "✓ MCP server is running on port 3001"
        return 0
    fi
    
    echo "⚠️  WARNING: MCP server is not running!"
    echo "The agent requires the MCP server to be running locally."
    echo ""
    echo "To start MCP server:"
    echo "  Option 1: cd pms_mcp_server && npm run dev"
    echo "  Option 2: Use ./agent/deploy-with-mcp.sh for automatic setup"
    echo "  Option 3: sudo ./agent/setup-mcp-production.sh for production setup"
    echo ""
    read -p "Continue deployment anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

# Check MCP server before deployment
check_mcp_server

echo "Building Docker image..."
cd agent

# Ensure environment variables are set
if [ -f ".env" ]; then
    echo "Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
fi

docker build -t livekitsdr-agent .

echo "Tagging image for ACR..."
docker tag livekitsdr-agent livekitsdracr.azurecr.io/livekit-agent:latest

echo "Logging in to Azure Container Registry..."
az acr login --name livekitsdracr

echo "Pushing image to ACR..."
docker push livekitsdracr.azurecr.io/livekit-agent:latest

# Update Azure App Service configuration for MCP
echo "Updating Azure App Service configuration..."
az webapp config appsettings set \
    --name livekitsdr-agent \
    --resource-group livekitsdr-rg \
    --settings \
    PMS_MCP_SERVER_URL="${PMS_MCP_SERVER_URL:-http://localhost:3001}" \
    PMS_MCP_SERVER_TOKEN="$PMS_MCP_SERVER_TOKEN" \
    --output none

echo "Restarting Azure App Service to use new image..."
az webapp restart --name livekitsdr-agent --resource-group livekitsdr-rg

echo "================================================"
echo "Deployment complete!"
echo "Agent URL: https://livekitsdr-agent.azurewebsites.net"
echo "MCP Server: ${PMS_MCP_SERVER_URL:-http://localhost:3001}"
echo "================================================"