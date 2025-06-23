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

The workflow will:
1. Create `.env` file from GitHub secrets
2. Create Google service account JSON from `GOOGLE_SERVICE_ACCOUNT_JSON` secret
3. Build and push the Docker image
4. Deploy to Azure Container Instances

#### Required GitHub Secrets

Add these secrets to your repository:
- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `AZURE_OPENAI_DEPLOYMENT_NAME_MINI`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_SPEECH_KEY`
- `AZURE_SPEECH_REGION`
- `ASSEMBLYAI_API_KEY`
- `CARTESIA_API_KEY`
- `GOOGLE_SERVICE_ACCOUNT_JSON` - The entire contents of your Google service account JSON file
- `GOOGLE_CALENDAR_ID`
- `GOOGLE_DELEGATED_USER_EMAIL`
- `SUPABASE_URL` (optional)
- `SUPABASE_KEY` (optional)
- `ACR_USERNAME`
- `ACR_PASSWORD`
- `AZURE_CREDENTIALS`

## Security Notes

- Never commit `.env` or `botelai-*.json` files to Git
- These files are excluded by `.gitignore`
- The Docker image includes these files, so treat the image as sensitive
- Consider using Azure Key Vault for production credentials