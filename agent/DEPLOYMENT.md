# Agent Deployment Guide

## Local Development

1. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

2. Ensure the Google service account JSON file is in the agent directory:
   - File should be named: `botelai-d95567fc3ae3.json`
   - This file contains Google Calendar API credentials

3. Run the agent locally:
   ```bash
   python agent.py start
   ```

## Production Deployment

The agent uses environment variables from a `.env` file that's included in the Docker image.

### Manual Deployment

1. Ensure you have:
   - `.env` file with all credentials
   - `botelai-d95567fc3ae3.json` Google service account file

2. Build and push the Docker image:
   ```bash
   ./build-and-push.sh
   ```

3. Deploy to Azure Container Instances:
   ```bash
   az container create \
     --resource-group livekitsdr-rg \
     --name livekitsdr-agent-container \
     --image livekitsdracr.azurecr.io/livekitsdr-agent:latest \
     --registry-login-server livekitsdracr.azurecr.io \
     --registry-username livekitsdracr \
     --registry-password "YOUR_ACR_PASSWORD" \
     --cpu 1 \
     --memory 1.5 \
     --restart-policy Always \
     --os-type Linux \
     --location eastus
   ```

### Automated Deployment

GitHub Actions will automatically deploy when you push to the `agent/` directory.

**Important**: The GitHub Actions workflow expects the Docker image to already contain the `.env` and Google service account files. You must build and push the image manually first using `./build-and-push.sh`.

## Security Notes

- Never commit `.env` or `botelai-*.json` files to Git
- These files are excluded by `.gitignore`
- The Docker image includes these files, so treat the image as sensitive
- Consider using Azure Key Vault for production credentials