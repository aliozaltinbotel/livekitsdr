#!/bin/bash

# Deploy Python agent with local MCP server support
# This script ensures the PMS MCP server is running locally before deployment

set -e  # Exit on error

echo "================================================"
echo "Deploying LiveKit Agent with MCP Server Support"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "agent.py" ]; then
    echo "Error: This script must be run from the agent directory"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    lsof -i:$1 > /dev/null 2>&1
}

# Function to start MCP server
start_mcp_server() {
    echo "Starting PMS MCP Server..."
    cd pms_mcp_server
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment for MCP server..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    echo "Installing MCP server dependencies..."
    pip install -r requirements.txt
    
    # Check if MCP server is already running
    if check_port 3001; then
        echo "MCP server is already running on port 3001"
    else
        # Start MCP server in background
        echo "Starting MCP server in background..."
        python -m src > mcp-server.log 2>&1 &
        MCP_PID=$!
        echo "MCP server started with PID: $MCP_PID"
        
        # Wait for server to be ready
        echo "Waiting for MCP server to be ready..."
        for i in {1..30}; do
            if check_port 3001; then
                echo "MCP server is ready!"
                break
            fi
            sleep 1
        done
        
        if ! check_port 3001; then
            echo "Error: MCP server failed to start. Check mcp-server.log for details"
            exit 1
        fi
    fi
    
    cd - > /dev/null
}

# Function to check environment variables
check_env_vars() {
    echo "Checking environment variables..."
    
    # Required vars for MCP
    if [ -z "$PMS_MCP_SERVER_URL" ]; then
        export PMS_MCP_SERVER_URL="http://localhost:3001"
        echo "Set PMS_MCP_SERVER_URL=$PMS_MCP_SERVER_URL"
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo "Warning: .env file not found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo "Please update .env with your credentials"
            exit 1
        else
            echo "Error: No .env or .env.example file found"
            exit 1
        fi
    fi
    
    # Source .env file
    export $(cat .env | grep -v '^#' | xargs)
}

# Function to test MCP connection
test_mcp_connection() {
    echo "Testing MCP server connection..."
    if python test_mcp.py; then
        echo "MCP server connection test passed!"
    else
        echo "Warning: MCP server connection test failed"
        echo "Continuing with deployment..."
    fi
}

# Main deployment process
main() {
    # Step 1: Check environment
    check_env_vars
    
    # Step 2: Start MCP server
    start_mcp_server
    
    # Step 3: Test MCP connection (optional)
    if [ -f "test_mcp.py" ]; then
        test_mcp_connection
    fi
    
    # Step 4: Build Docker image
    echo "Building Docker image..."
    docker build -t livekitsdr-agent .
    
    # Step 5: Tag for Azure Container Registry
    echo "Tagging image for ACR..."
    docker tag livekitsdr-agent livekitsdracr.azurecr.io/livekit-agent:latest
    
    # Step 6: Login to Azure
    echo "Logging in to Azure Container Registry..."
    az acr login --name livekitsdracr
    
    # Step 7: Push to ACR
    echo "Pushing image to ACR..."
    docker push livekitsdracr.azurecr.io/livekit-agent:latest
    
    # Step 8: Update Azure App Service configuration
    echo "Updating Azure App Service configuration..."
    az webapp config appsettings set \
        --name livekitsdr-agent \
        --resource-group livekitsdr-rg \
        --settings \
        PMS_MCP_SERVER_URL="$PMS_MCP_SERVER_URL" \
        PMS_MCP_SERVER_TOKEN="$PMS_MCP_SERVER_TOKEN"
    
    # Step 9: Restart App Service
    echo "Restarting Azure App Service..."
    az webapp restart --name livekitsdr-agent --resource-group livekitsdr-rg
    
    echo "================================================"
    echo "Deployment complete!"
    echo "Agent URL: https://livekitsdr-agent.azurewebsites.net"
    echo "MCP Server: Running locally on port 3001"
    echo "================================================"
    
    # Show MCP server logs
    echo ""
    echo "Recent MCP server logs:"
    tail -n 20 ../pms_mcp_server/mcp-server.log || true
}

# Run main function
main

# Keep script running to show MCP server output
echo ""
echo "Press Ctrl+C to stop the MCP server and exit"
wait