# Botel AI Property Manager Agent

## Overview

The Botel AI agent has been updated to function as an AI-powered short-term rental property manager. This agent can answer questions about rental properties, provide property details, assist with check-in procedures, and offer local area information.

## Key Features

### 1. **Property Information Access**
- Fetches real-time property data via MCP (Model Context Protocol) integration
- Provides details about:
  - Property locations and addresses
  - Capacity and occupancy limits
  - Amenities and features
  - Property status (active/inactive)
  - Detailed descriptions

### 2. **Guest Services**
- Answers common guest questions:
  - Check-in/check-out procedures
  - WiFi passwords and connectivity
  - Parking information
  - House rules and policies
  - Local area recommendations

### 3. **Natural Conversation Flow**
- Maintains friendly, professional tone
- Responds immediately without "processing" delays
- Handles interruptions gracefully
- Prompts gently after silence

## MCP Integration

The agent uses the PMS MCP Server to access property data:

### Configuration
```env
# In agent/.env
PMS_MCP_SERVER_URL=http://localhost:3001
PMS_MCP_SERVER_TOKEN=<your-token>
```

### Available Tool
- `get_customer_properties_context`: Fetches comprehensive property information
  - Parameters: `include_inactive` (boolean, default: false)
  - Returns: Formatted property context with all details

## Common Use Cases

### 1. Property Inquiry
**Guest**: "What properties do you have?"
**Agent**: Uses MCP tool to fetch and present property portfolio

### 2. Specific Property Details
**Guest**: "Tell me about the beach house"
**Agent**: Provides location, capacity, amenities for that specific property

### 3. Check-in Information
**Guest**: "What time is check-in?"
**Agent**: "Check-in is typically at 3:00 PM and check-out is at 11:00 AM..."

### 4. Amenities
**Guest**: "Is there WiFi?"
**Agent**: Checks property-specific amenities and responds accordingly

### 5. Local Recommendations
**Guest**: "Any good restaurants nearby?"
**Agent**: Provides area-specific recommendations based on property location

## Testing

### Run the MCP Test Script
```bash
cd agent
python test_mcp.py
```

This will verify:
- MCP server connection
- Tool availability
- Agent configuration

### Test Locally

#### Option 1: Manual Setup
```bash
# Terminal 1: Start the PMS MCP Server
cd agent/pms_mcp_server
source venv/bin/activate  # or create: python3 -m venv venv
pip install -r requirements.txt
MCP_MODE=http python -m src

# Terminal 2: Start the LiveKit agent
cd agent
python agent.py dev

# Terminal 3: Start the frontend
cd frontend
npm run dev
```

#### Option 2: Using Deployment Script
```bash
cd agent
./deploy-with-mcp.sh
```

#### Option 3: Using Docker Compose
```bash
# Copy and configure environment
cp .env.docker .env
# Edit .env with your credentials

# Start all services
docker-compose up

# Or just agent and MCP server
docker-compose up mcp-server livekit-agent
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│  LiveKit Agent  │────▶│  MCP Server      │────▶│  PMS API        │
│  (Property Mgr) │     │  (localhost:3001)│     │  (Botel API)    │
│                 │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                                                  
        │                                                  
        ▼                                                  
┌─────────────────┐                                       
│                 │                                       
│  Guest/Owner    │                                       
│  (Voice/Text)   │                                       
│                 │                                       
└─────────────────┘                                       
```

## Deployment Notes

### Production Deployment

1. **Setup MCP Server as System Service**:
   ```bash
   sudo ./agent/setup-mcp-production.sh
   ```

2. **Deploy Agent to Azure**:
   ```bash
   ./deploy-agent.sh
   ```
   The script will:
   - Check if MCP server is running locally
   - Build and push Docker image
   - Update Azure App Service configuration
   - Set MCP server URL and authentication

3. **Environment Variables**:
   - `PMS_MCP_SERVER_URL`: URL where MCP server is accessible (default: http://localhost:3001)
   - `PMS_MCP_SERVER_TOKEN`: Authentication token for MCP server
   - `PMS_API_KEY`: API key for accessing PMS backend
   - `PMS_API_URL`: PMS API endpoint (default: https://api-dev.botel.ai)

4. **Security Considerations**:
   - MCP server should only be accessible from the agent
   - Use authentication tokens in production
   - Consider VPN or private networking for MCP-Agent communication
   - Regularly rotate API keys and tokens

## Future Enhancements

- Booking integration
- Real-time availability checking
- Maintenance request handling
- Multi-language support
- Dynamic pricing information