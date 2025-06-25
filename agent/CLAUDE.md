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

### Best Practices & Optimal Parameters (v1.1.4 - June 2025)

#### AssemblyAI STT - Universal Streaming
```python
stt=assemblyai.STT(
    api_key=os.getenv("ASSEMBLYAI_API_KEY"),
    sample_rate=16000,           # 16kHz optimal for voice agents
    encoding="pcm_s16le",        # Best quality encoding
    buffer_size_seconds=0.05,    # 50ms for low latency
    # Turn detection parameters (v1.1.4):
    end_of_turn_confidence_threshold=0.65,  # 0.4-1.0, higher = more conservative
    min_end_of_turn_silence_when_confident=160,  # ms of silence when confident
    max_turn_silence=2400,       # Max silence before forced turn end (ms)
    format_turns=True,           # Clean transcript formatting
)
```

**Key Features**:
- Linguistic turn detection model (audio + semantic understanding)
- ~300ms immutable transcript latency
- Handles complex pauses (e.g., "My credit card is...")

#### OpenAI LLM - GPT-4o-mini
```python
llm=openai.LLM(
    model="gpt-4o-mini",         # 2x faster than gpt-4o, 83% cheaper
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,             # Range: 0.6-1.2 for voice agents
    # Optional parameters (v1.1.4):
    # parallel_tool_calls=True,  # Enable parallel function calls
    # max_completion_tokens=150, # Limit response length
    # user="unique-user-id",     # For tracking
)
```

**Performance**: ~300ms response time (human speech threshold)

#### Cartesia TTS - Sonic Turbo
```python
tts=cartesia.TTS(
    api_key=os.getenv("CARTESIA_API_KEY"),
    model="sonic-turbo",         # 40ms latency (fastest)
    voice="248be419-c632-4f23-adf1-5324ed7dbf1d",  # Professional voice
    language="en",
    speed=0.1,                   # Slight speed increase for energy
    emotion=["positivity:high", "curiosity:medium"],  # v1.1.4 feature
    # Native sample_rate=24000, encoding="pcm_s16le" (defaults)
)
```

**Alternative**: Use `model="sonic-2"` for standard quality

#### Silero VAD - Optimized Settings
```python
vad=silero.VAD.load(
    min_speech_duration=0.15,    # 150ms to start detection
    min_silence_duration=0.55,   # 550ms for natural pauses
    prefix_padding_duration=0.3, # 300ms context padding
    activation_threshold=0.5,    # Balanced sensitivity
    sample_rate=16000,          # Must match STT
    force_cpu=True,             # Consistent performance
)
```

**Performance**: <1ms per 30ms audio chunk on CPU

#### AgentSession Configuration
```python
session = AgentSession(
    stt=assemblyai.STT(...),
    llm=openai.LLM(...),
    tts=cartesia.TTS(...),
    vad=silero.VAD.load(...),
    turn_detection="stt",        # AssemblyAI's linguistic model
    min_endpointing_delay=0.3,   # 300ms for responsiveness
)
```

### Latency Benchmarks (v1.1.4)
- **First syllable**: ~730ms total
- **STT**: ~300ms (AssemblyAI)
- **LLM**: ~300ms (GPT-4o-mini)
- **TTS**: ~40ms (Sonic Turbo)
- **Network/Processing**: ~90ms

### NOT SUPPORTED Parameters (Removed in v1.1.4):
- AssemblyAI STT: `word_boost`, `disable_partial_transcripts`, `enable_extra_session_information`, `end_utterance_silence_threshold` (old parameter)
- OpenAI LLM: `max_tokens` (use `max_completion_tokens` instead)
- AgentSession: `interrupt_speech_on_user_speech`
- Silero VAD: `padding_duration` (deprecated, use `prefix_padding_duration`)

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