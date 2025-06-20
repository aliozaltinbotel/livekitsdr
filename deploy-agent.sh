#!/bin/bash

# Build and deploy Python agent to Azure

echo "Building Docker image..."
cd agent
docker build -t livekitsdr-agent .

echo "Tagging image for ACR..."
docker tag livekitsdr-agent livekitsdracr.azurecr.io/livekit-agent:latest

echo "Logging in to Azure Container Registry..."
az acr login --name livekitsdracr

echo "Pushing image to ACR..."
docker push livekitsdracr.azurecr.io/livekit-agent:latest

echo "Restarting Azure App Service to use new image..."
az webapp restart --name livekitsdr-agent --resource-group livekitsdr-rg

echo "Deployment complete!"
echo "Agent URL: https://livekitsdr-agent.azurewebsites.net"