#!/bin/bash

# Build and push agent Docker image with local .env file

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found in agent directory"
    echo "Please create .env file with required environment variables"
    exit 1
fi

# Check if Google service account file exists
if [ ! -f "botelai-d95567fc3ae3.json" ]; then
    echo "Error: Google service account file not found"
    echo "Please ensure botelai-d95567fc3ae3.json is in the agent directory"
    exit 1
fi

# Login to Azure Container Registry
echo "Logging in to Azure Container Registry..."
az acr login --name livekitsdracr

# Build the Docker image
echo "Building Docker image..."
docker build -t livekitsdracr.azurecr.io/livekitsdr-agent:latest .

# Push to registry
echo "Pushing image to registry..."
docker push livekitsdracr.azurecr.io/livekitsdr-agent:latest

echo "Build and push completed successfully!"