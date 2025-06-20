#!/bin/bash

# Azure Services Setup Script for LiveKit Agent
# This script creates all required Azure resources and outputs the configuration

set -e

echo "🚀 Setting up Azure Services for LiveKit Agent..."

# Variables
RESOURCE_GROUP="livekitsdr-rg"
LOCATION="eastus"
OPENAI_NAME="livekitsdr-openai-$(date +%s)"
SPEECH_NAME="livekitsdr-speech-$(date +%s)"
DEPLOYMENT_NAME="gpt-4o-deployment"

# Check if logged in to Azure
echo "📝 Checking Azure login status..."
if ! az account show &>/dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

# Get current subscription
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "✅ Using subscription: $SUBSCRIPTION_ID"

# Check if resource group exists, create if not
echo "📦 Checking resource group..."
if ! az group show --name $RESOURCE_GROUP &>/dev/null; then
    echo "Creating resource group: $RESOURCE_GROUP"
    az group create --name $RESOURCE_GROUP --location $LOCATION
else
    echo "✅ Resource group exists: $RESOURCE_GROUP"
fi

# Create Azure OpenAI Service
echo "🤖 Creating Azure OpenAI Service..."
echo "Note: Azure OpenAI requires approval. If this fails, you may need to request access."

# Check if OpenAI resource exists
if az cognitiveservices account show --name $OPENAI_NAME --resource-group $RESOURCE_GROUP &>/dev/null; then
    echo "✅ OpenAI resource already exists"
else
    az cognitiveservices account create \
        --name $OPENAI_NAME \
        --resource-group $RESOURCE_GROUP \
        --kind OpenAI \
        --sku S0 \
        --location $LOCATION \
        --yes
    
    echo "⏳ Waiting for OpenAI resource to be ready..."
    sleep 30
fi

# Get OpenAI endpoint and key
OPENAI_ENDPOINT=$(az cognitiveservices account show \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.endpoint \
    -o tsv)

OPENAI_KEY=$(az cognitiveservices account keys list \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --query key1 \
    -o tsv)

# Deploy GPT-4o model
echo "🚀 Deploying GPT-4o model..."
echo "Note: This may fail if your subscription doesn't have access to GPT-4o"

# Check if deployment exists
if az cognitiveservices account deployment show \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --deployment-name $DEPLOYMENT_NAME &>/dev/null; then
    echo "✅ Deployment already exists"
else
    # Try gpt-4o first, fall back to gpt-35-turbo if not available
    if az cognitiveservices account deployment create \
        --name $OPENAI_NAME \
        --resource-group $RESOURCE_GROUP \
        --deployment-name $DEPLOYMENT_NAME \
        --model-name gpt-4o \
        --model-version "2024-05-13" \
        --model-format OpenAI \
        --sku-capacity 10 \
        --sku-name "Standard" 2>/dev/null; then
        echo "✅ GPT-4o deployed successfully"
        MODEL_NAME="gpt-4o"
    else
        echo "⚠️  GPT-4o not available, trying GPT-3.5-Turbo..."
        DEPLOYMENT_NAME="gpt-35-turbo-deployment"
        az cognitiveservices account deployment create \
            --name $OPENAI_NAME \
            --resource-group $RESOURCE_GROUP \
            --deployment-name $DEPLOYMENT_NAME \
            --model-name gpt-35-turbo \
            --model-version "0613" \
            --model-format OpenAI \
            --sku-capacity 10 \
            --sku-name "Standard"
        MODEL_NAME="gpt-35-turbo"
    fi
fi

# Create Azure Speech Service
echo "🎤 Creating Azure Speech Service..."

# Check if Speech resource exists
if az cognitiveservices account show --name $SPEECH_NAME --resource-group $RESOURCE_GROUP &>/dev/null; then
    echo "✅ Speech resource already exists"
else
    az cognitiveservices account create \
        --name $SPEECH_NAME \
        --resource-group $RESOURCE_GROUP \
        --kind SpeechServices \
        --sku S0 \
        --location $LOCATION \
        --yes
fi

# Get Speech key and region
SPEECH_KEY=$(az cognitiveservices account keys list \
    --name $SPEECH_NAME \
    --resource-group $RESOURCE_GROUP \
    --query key1 \
    -o tsv)

SPEECH_REGION=$LOCATION

# Output results
echo ""
echo "✅ Azure services created successfully!"
echo ""
echo "📋 Add these secrets to your GitHub repository:"
echo "================================================"
echo ""
echo "AZURE_OPENAI_API_KEY=$OPENAI_KEY"
echo "AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT"
echo "AZURE_OPENAI_DEPLOYMENT_NAME=$DEPLOYMENT_NAME"
echo "AZURE_OPENAI_API_VERSION=2024-02-01"
echo "AZURE_SPEECH_KEY=$SPEECH_KEY"
echo "AZURE_SPEECH_REGION=$SPEECH_REGION"
echo ""
echo "================================================"
echo ""
echo "📝 Resource Details:"
echo "- Resource Group: $RESOURCE_GROUP"
echo "- OpenAI Resource: $OPENAI_NAME"
echo "- Speech Resource: $SPEECH_NAME"
echo "- Model: $MODEL_NAME"
echo "- Location: $LOCATION"
echo ""

# Save to file for reference
OUTPUT_FILE="azure-credentials.txt"
cat > $OUTPUT_FILE << EOF
# Azure Credentials for LiveKit Agent
# Generated: $(date)
# DO NOT COMMIT THIS FILE TO GIT

AZURE_OPENAI_API_KEY=$OPENAI_KEY
AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT_NAME=$DEPLOYMENT_NAME
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_SPEECH_KEY=$SPEECH_KEY
AZURE_SPEECH_REGION=$SPEECH_REGION

# Resource Details
RESOURCE_GROUP=$RESOURCE_GROUP
OPENAI_RESOURCE=$OPENAI_NAME
SPEECH_RESOURCE=$SPEECH_NAME
MODEL=$MODEL_NAME
EOF

echo "💾 Credentials saved to: $OUTPUT_FILE"
echo ""
echo "⚠️  IMPORTANT: Add $OUTPUT_FILE to .gitignore!"
echo ""
echo "🎯 Next steps:"
echo "1. Copy the credentials above to your GitHub Secrets"
echo "2. Update GOOGLE_CALENDAR_ID and GOOGLE_DELEGATED_USER_EMAIL in GitHub Secrets"
echo "3. Push changes to trigger deployment"