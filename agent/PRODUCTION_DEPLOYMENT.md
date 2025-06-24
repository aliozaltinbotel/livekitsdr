# Production Deployment Guide

This guide covers deploying the LiveKit Agent with integrated MCP Server to production using GitHub Actions.

## Architecture Overview

The production deployment consists of a single container running:
1. **MCP Server**: Provides property management system integration (port 3001)
2. **LiveKit Agent**: Voice agent with AI capabilities
3. **Azure Container Instances**: Hosts the container with both services

## Prerequisites

### Required Azure Resources
- Azure Container Registry (ACR)
- Azure Resource Group
- Azure Virtual Network (for private communication between containers)
- Azure Container Instances

### Required Secrets in GitHub

Configure these secrets in your GitHub repository settings:

#### Azure Credentials
- `AZURE_CREDENTIALS`: Service principal credentials for Azure CLI
- `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID
- `ACR_USERNAME`: Azure Container Registry username
- `ACR_PASSWORD`: Azure Container Registry password

#### LiveKit Configuration
- `LIVEKIT_URL`: Your LiveKit server URL
- `LIVEKIT_API_KEY`: LiveKit API key
- `LIVEKIT_API_SECRET`: LiveKit API secret

#### AI Services
- `OPENAI_API_KEY`: OpenAI API key
- `DEEPGRAM_API_KEY`: Deepgram API key (optional)
- `ASSEMBLYAI_API_KEY`: AssemblyAI API key
- `CARTESIA_API_KEY`: Cartesia API key for TTS

#### Google Calendar (Optional)
- `GOOGLE_SERVICE_ACCOUNT_JSON`: Service account JSON file contents
- `GOOGLE_CALENDAR_ID`: Calendar ID (usually "primary")
- `GOOGLE_DELEGATED_USER_EMAIL`: Email for domain-wide delegation

#### Supabase (Optional)
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase anon key

#### PMS Integration
- `PMS_BASE_URL`: Property Management System API URL
- `PMS_API_KEY`: PMS API key
- `MCP_AUTH_TOKEN`: Authentication token for MCP server

## Deployment Process

### Automatic Deployment

The deployment workflow triggers automatically when:
- Code is pushed to the `main` branch
- Changes are detected in the `agent/` directory
- The workflow file itself is modified

### Manual Deployment

You can manually trigger deployment from GitHub Actions:

1. Go to Actions → Deploy Agent to Production
2. Click "Run workflow"
3. The workflow will build and deploy the container with both services

### Deployment Steps

The workflow performs these steps:

1. **Build Container**
   - Builds Docker image with both agent and MCP server
   - Includes all dependencies for both services
   - Includes Google service account credentials
   - Pushes to Azure Container Registry with caching

2. **Deploy Container**
   - Creates single container instance
   - Configures all environment variables
   - Sets up health checks for MCP server
   - Allocates 1.5 CPU and 2GB memory

3. **Start Services**
   - Startup script launches MCP server first
   - Waits for MCP server to be ready
   - Launches LiveKit agent
   - Both services run in same container

4. **Validate Deployment**
   - Checks container status
   - Verifies services are running
   - Reports deployment health

## Environment Variables

All environment variables are configured in the single container:

```bash
# LiveKit Configuration
LIVEKIT_URL           # LiveKit server WebSocket URL
LIVEKIT_API_KEY       # LiveKit API key
LIVEKIT_API_SECRET    # LiveKit API secret

# AI Services
OPENAI_API_KEY        # OpenAI API key
ASSEMBLYAI_API_KEY    # AssemblyAI API key
CARTESIA_API_KEY      # Cartesia TTS API key
DEEPGRAM_API_KEY      # Deepgram API key (optional)

# PMS Integration
PMS_BASE_URL          # PMS API base URL
PMS_API_KEY           # PMS API authentication key
MCP_AUTH_TOKEN        # Bearer token for MCP authentication
PMS_MCP_SERVER_URL    # Auto-set to http://localhost:3001/sse

# Google Calendar (Optional)
GOOGLE_SERVICE_ACCOUNT_KEY    # Path to service account JSON
GOOGLE_CALENDAR_ID            # Calendar ID
GOOGLE_DELEGATED_USER_EMAIL   # Email for delegation

# Supabase (Optional)
SUPABASE_URL          # Supabase project URL
SUPABASE_KEY          # Supabase anon key

# Production Settings
ENVIRONMENT           # Set to "production"
LOG_LEVEL             # Logging level (INFO/DEBUG/WARNING/ERROR)
```

## Security Considerations

### Network Security
- MCP server only accessible via localhost within container
- No external ports exposed for MCP
- Agent communicates with MCP over localhost:3001

### Container Security
- Single container reduces attack surface
- Minimal base image (python:3.11-slim)
- Health checks for MCP server
- Auto-restart on failure

### Secrets Management
- All sensitive data stored in GitHub Secrets
- No secrets committed to repository
- Service account JSON injected at build time

## Monitoring and Debugging

### View Container Logs
```bash
# View combined logs (both services)
az container logs --resource-group livekitsdr-rg --name livekitsdr-agent-container

# View recent logs
az container logs --resource-group livekitsdr-rg --name livekitsdr-agent-container --tail 100

# Follow logs in real-time
az container logs --resource-group livekitsdr-rg --name livekitsdr-agent-container --follow
```

### Check Container Status
```bash
# Check container status
az container show --resource-group livekitsdr-rg --name livekitsdr-agent-container --query instanceView.state

# Check detailed container info
az container show --resource-group livekitsdr-rg --name livekitsdr-agent-container
```

### Service Health
- MCP server health check runs automatically
- Container restarts if health check fails
- Logs show "MCP server is ready!" when healthy
- Logs show "Starting LiveKit agent..." when agent starts

## Troubleshooting

### Container Won't Start
1. Check logs for error messages
2. Verify all required environment variables are set
3. Ensure ACR credentials are correct
4. Check resource limits (CPU/Memory)
5. Look for "MCP server is ready!" in logs

### MCP Server Issues
1. Check if port 3001 is accessible within container
2. Verify PMS_API_KEY is set correctly
3. Look for MCP startup errors in logs
4. Ensure health check is passing

### Agent Connection Issues
1. Check LiveKit credentials
2. Verify API keys are valid
3. Ensure MCP server started before agent
4. Review agent logs for errors

## Rollback Procedure

To rollback to a previous version:

1. Find the previous commit SHA
2. Update container image:
```bash
# Rollback to previous version
az container create ... --image livekitsdracr.azurecr.io/livekitsdr-agent:<previous-sha>
```

## Local Development

For local development with production-like setup:

1. Copy `.env.example` to `.env`
2. Fill in your credentials
3. Run MCP server locally:
   ```bash
   cd agent/pms_mcp_server
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m src.sse_server
   ```
4. Run agent:
   ```bash
   cd agent
   python agent.py
   ```

## Performance Optimization

### Container Resources
- Combined container: 1.5 CPU, 2GB RAM
- MCP server uses minimal resources for API calls
- Agent uses majority of resources for voice processing

### Scaling Considerations
- Each container instance handles one concurrent call
- Scale horizontally by creating multiple containers
- Each container runs its own MCP server instance
- No shared state between containers

## Startup Sequence

The container startup follows this sequence:
1. MCP server starts on port 3001
2. Health check verifies MCP is ready
3. Agent starts with localhost MCP connection
4. Both services run in parallel

## Backup and Recovery

### Configuration Backup
Keep backups of:
- Environment variable configurations
- GitHub Secrets
- Container settings
- Startup script

### Data Persistence
- Container is stateless
- Agent uses Supabase for conversation logs
- MCP server queries PMS API in real-time
- No local data storage required