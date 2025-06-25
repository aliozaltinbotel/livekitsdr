# LiveKit SDR Agent - Development Memory

## Important Configuration Notes

### ⚠️ ALWAYS CHECK SDK DOCUMENTATION BEFORE ADDING PARAMETERS

Many parameters shown in online documentation or examples may not be supported in the current SDK version.

### 📦 SDK Versions (Updated: June 25, 2025)

All LiveKit packages should be at version **1.1.4** or higher:
- `livekit-agents[mcp]>=1.1.4`
- `livekit-plugins-openai>=1.1.4`
- `livekit-plugins-azure>=1.1.4`
- `livekit-plugins-silero>=1.1.4`
- `livekit-plugins-assemblyai>=1.1.4`
- `livekit-plugins-cartesia>=1.1.4`

To check for updates:
```bash
pip list --outdated | grep livekit
```

### Verified Working Parameters (as of June 2025)

#### AssemblyAI STT
```python
stt=assemblyai.STT(
    api_key=os.getenv("ASSEMBLYAI_API_KEY"),  # Optional if env var is set
    sample_rate=16000,                         # Audio sample rate
    encoding="pcm_s16le",                      # Audio encoding format
    buffer_size_seconds=0.05,                  # Buffer size for frames
)
```

**NOT SUPPORTED** (despite being in some docs):
- `word_boost`
- `disable_partial_transcripts`
- `enable_extra_session_information`
- `end_utterance_silence_threshold`

#### OpenAI LLM
```python
llm=openai.LLM(
    model="gpt-4o-mini",                      # Model name
    api_key=os.getenv("OPENAI_API_KEY"),      # API key
    temperature=0.5,                          # Temperature for responses
)
```

**NOT SUPPORTED**:
- `max_tokens`

#### AgentSession
```python
session = AgentSession(
    stt=assemblyai.STT(...),
    llm=openai.LLM(...),
    tts=cartesia.TTS(...),
    vad=silero.VAD.load(...),
    turn_detection="stt",  # Use AssemblyAI's linguistic turn detection
)
```

**NOT SUPPORTED**:
- `interrupt_speech_on_user_speech`

### MCP Server JSON-RPC Implementation

The MCP server must handle:
1. Nested message structures from LiveKit's MCP client
2. Protocol version matching (use client-requested version)
3. Proper id field handling (never return None)
4. JSON serialization of response objects

### Testing Commands

Always test locally before deploying:
```bash
# Run lint and typecheck
npm run lint
npm run typecheck

# Test MCP server
cd pms_mcp_server
python -m src.sse_server
```

### Critical Issues Fixed

1. **Agent not joining rooms**: Removed custom `job_request_handler` - use default auto-accept
2. **MCP server communication**: Fixed JSON-RPC parsing and response format
3. **Parameter errors**: Removed unsupported SDK parameters
4. **Response truncation**: Adjusted STT and LLM settings for better streaming

### Environment Variables Required

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `OPENAI_API_KEY`
- `ASSEMBLYAI_API_KEY`
- `CARTESIA_API_KEY`
- `PMS_API_KEY` (for property data)
- `SUPABASE_URL` (optional, for logging)
- `SUPABASE_KEY` (optional, for logging)

### Deployment Notes

1. MCP server runs on port 3001 inside the container
2. Agent connects to MCP via `http://localhost:3001/sse`
3. Both services start via `start_production.sh`
4. Health check endpoint: `http://localhost:3001/health`