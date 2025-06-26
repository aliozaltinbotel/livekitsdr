# LiveKit SDR Voice Agent

A production-ready AI-powered voice agent built with LiveKit framework for property management and guest inquiries.

## Features

- 🎙️ Real-time voice conversations with AI assistant
- 🏠 Property Management System (PMS) integration via MCP server
- 📅 Google Calendar integration for scheduling
- 📊 Conversation analytics with Supabase
- 🔊 Multiple STT/TTS provider support (AssemblyAI, Cartesia, OpenAI, Azure)
- 🚀 Production-ready with Azure Container deployment

## Architecture

- **LiveKit Agent**: Voice conversation handling with AI
- **MCP Server**: Property management system integration (port 3001)  
- **Supabase**: Session logging and analytics
- **Azure Container**: Production deployment platform

## Prerequisites

- Python 3.9+
- LiveKit Cloud account
- Required API keys (see Environment Variables)
- Azure account (for production deployment)

## Quick Start

### 1. Clone the repository
```bash
git clone <repository-url>
cd livekitsdr/agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. Run locally
```bash
# Start MCP server (SSE version for LiveKit)
cd pms_mcp_server
python -m src.sse_server

# In another terminal, start the agent
python agent.py start
```

### 5. Cursor IDE Integration (Optional)
For local development with Cursor IDE, add to MCP settings:
```json
{
  "mcpServers": {
    "pms-local": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/pms_mcp_server",
      "env": {
        "PMS_API_KEY": "your-bearer-token",
        "PMS_CUSTOMER_ID": "your-customer-id"
      }
    }
  }
}
```

## Environment Variables

### Required
```bash
# LiveKit Configuration
LIVEKIT_URL=your-livekit-url
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# AI Services  
OPENAI_API_KEY=your-openai-key
ASSEMBLYAI_API_KEY=your-assemblyai-key
CARTESIA_API_KEY=your-cartesia-key

# PMS Integration
PMS_BASE_URL=https://pms.botel.ai
PMS_API_KEY=your-pms-key
PMS_MCP_SERVER_URL=http://localhost:3001/sse
```

### Optional
```bash
# Azure AI Services
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_SPEECH_KEY=your-speech-key

# Google Calendar
GOOGLE_SERVICE_ACCOUNT_JSON=path-to-json
GOOGLE_CALENDAR_ID=your-calendar-id

# Supabase Analytics
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

## Production Deployment

### Automatic Deployment
Pushing to the `agent/` directory triggers GitHub Actions to build and deploy.

### Manual Deployment
```bash
./build-and-push.sh
```

### Container Configuration
- **CPU**: 1.5 cores
- **RAM**: 2GB
- **Port**: 80 (HTTP)
- **Services**: MCP server + Agent in single container

## SDK Requirements

All LiveKit packages must be version **1.1.4** or higher:
- `livekit-agents[mcp]>=1.1.4`
- `livekit-plugins-openai>=1.1.4`
- `livekit-plugins-assemblyai>=1.1.4`
- `livekit-plugins-cartesia>=1.1.4`

## Optimal Configuration

### Voice Pipeline Configuration
```python
# STT: AssemblyAI
stt=assemblyai.STT(
    sample_rate=16000,
    buffer_size_seconds=0.05,
    end_of_turn_confidence_threshold=0.65,
    max_turn_silence=2400,
)

# LLM: OpenAI GPT-4o-mini
llm=openai.LLM(
    model="gpt-4o-mini",  # 2x faster, 83% cheaper
    temperature=0.7,
)

# TTS: Cartesia Sonic Turbo
tts=cartesia.TTS(
    model="sonic-turbo",  # 40ms latency
    voice="248be419-c632-4f23-adf1-5324ed7dbf1d",
    speed=0.1,
)
```

### Performance Benchmarks
- **First syllable latency**: ~730ms
- **STT**: ~300ms
- **LLM**: ~300ms  
- **TTS**: ~40ms

## Voice Agent Features

### Conversation Management
- Natural conversational flow without technical language
- Interruption handling with graceful recovery
- 3-attempt error recovery pattern
- Dynamic date parsing with current year

### MCP Tools Available
- `get_customer_properties_context`: Fetch property details
- `check_property_availability_and_pricing`: Check dates and pricing

### Property Information Access
The agent can provide:
- Property availability and pricing
- Amenities and features
- Check-in/out times and procedures
- WiFi credentials and door codes
- Property manager contact info

## Database Schema (Supabase)

### Tables
- **sessions**: Main session tracking with user data
- **conversations**: Message history with timestamps  
- **tool_calls**: Function call logs for debugging
- **session_summaries**: Aggregated view with metrics

### Example Query
```sql
-- Get recent sessions with conversation count
SELECT s.*, ss.message_count, ss.duration_seconds
FROM sessions s
JOIN session_summaries ss ON s.id = ss.session_id
ORDER BY s.created_at DESC
LIMIT 10;
```

## Monitoring & Debugging

### View Container Logs
```bash
az container logs --resource-group livekitsdr-rg \
  --name livekitsdr-agent-container --tail 100
```

### Check Container Status
```bash
az container show --resource-group livekitsdr-rg \
  --name livekitsdr-agent-container --query instanceView.state
```

### Key Log Patterns
- `MCP server is ready!` - MCP server started
- `Starting LiveKit agent...` - Agent initialization
- `Session started: [room_id]` - New conversation
- `Session data updated successfully` - Data saved

## Common Issues & Solutions

### Agent Not Joining Rooms
- Ensure using default auto-accept behavior
- Check LiveKit credentials in environment

### MCP Server Connection Failed
- Verify MCP server is running on port 3001
- Check PMS_API_KEY is valid

### Supabase Logging Errors
- Verify Supabase URL and key
- Check table schema matches expected format

## Security Best Practices

- Never commit `.env` files or service account JSON
- Store all credentials in GitHub Secrets
- Keep MCP server on localhost only
- Enable Row Level Security (RLS) in production
- Rotate API keys regularly

## Development Workflow

1. Make changes to agent code
2. Test locally with both services running
3. Run lint and type checks if available
4. Commit and push to trigger deployment
5. Monitor Azure logs for deployment status

## Future Enhancements

- [ ] Implement streaming responses when SDK supports it
- [ ] Add analytics dashboard for conversation insights
- [ ] Implement lead scoring based on patterns
- [ ] Add multi-language support
- [ ] Enhanced calendar integration features

## Support

For issues or questions:
- Check Azure container logs first
- Review environment variable configuration
- Ensure all services are running
- Check API key validity and permissions

## License

[Your License Here]