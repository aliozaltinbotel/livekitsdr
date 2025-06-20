#!/bin/bash

# Deploy GPT-4o-mini model to Azure OpenAI

set -e

echo "🚀 Deploying GPT-4o-mini to Azure OpenAI..."

RESOURCE_GROUP="livekitsdr-rg"
OPENAI_NAME="livekitsdr-openai-1750429425"
DEPLOYMENT_NAME="gpt-4o-mini-deployment"

# Check if deployment already exists
if az cognitiveservices account deployment show \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --deployment-name $DEPLOYMENT_NAME &>/dev/null; then
    echo "✅ GPT-4o-mini deployment already exists"
else
    echo "📦 Creating GPT-4o-mini deployment..."
    az cognitiveservices account deployment create \
        --name $OPENAI_NAME \
        --resource-group $RESOURCE_GROUP \
        --deployment-name $DEPLOYMENT_NAME \
        --model-name gpt-4o-mini \
        --model-version "2024-07-18" \
        --model-format OpenAI \
        --sku-capacity 50 \
        --sku-name "Standard"
    
    echo "✅ GPT-4o-mini deployed successfully"
fi

echo ""
echo "📝 Add this to your GitHub Secrets:"
echo "AZURE_OPENAI_DEPLOYMENT_NAME_MINI=$DEPLOYMENT_NAME"
echo ""
echo "🎯 This model is 2-3x faster than gpt-4o!"