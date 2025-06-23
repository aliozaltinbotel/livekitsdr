# AssemblyAI STT + Cartesia TTS Integration

This agent combines AssemblyAI's Universal Streaming STT with Cartesia's ultra-fast TTS for an optimized real-time voice experience.

## Usage

Run the agent with AssemblyAI STT and Cartesia TTS:
```bash
python agent_assemblyai.py
```

## Required Environment Variables

```bash
# AssemblyAI API Key (for STT)
ASSEMBLYAI_API_KEY=your-assemblyai-api-key

# Cartesia API Key (for TTS)
CARTESIA_API_KEY=your-cartesia-api-key

# Azure OpenAI variables (for LLM)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
AZURE_OPENAI_DEPLOYMENT_NAME_MINI=your-mini-deployment

# LiveKit credentials
LIVEKIT_URL=wss://your-instance.livekit.cloud
LIVEKIT_API_KEY=your-livekit-key
LIVEKIT_API_SECRET=your-livekit-secret
```

## Key Features

### AssemblyAI STT
- **Ultra-low latency**: ~300ms for real-time transcription
- **Intelligent turn detection**: Automatically detects when a speaker has finished
- **Word boosting**: Configured to boost recognition of domain-specific terms like "Botel AI", "Airbnb", etc.
- **Formatted transcripts**: Enabled for better conversation flow

### Cartesia TTS
- **Sonic Turbo model**: First audio byte in just 40ms
- **Professional voice**: Using voice ID `248be419-c632-4f23-adf1-5324ed7dbf1d`
- **Emotion control**: Set to "positivity:high" for friendly, professional tone
- **Normal speed**: Configured at 0.0 (normal speaking rate)

## Configuration Details

### AssemblyAI STT Configuration
- 16kHz sample rate (standard for telephony)
- Turn formatting enabled
- 0.7 confidence threshold for end-of-turn detection
- 160ms minimum silence for turn detection
- Word boost for property management terms

### Cartesia TTS Configuration
- Model: `sonic-turbo` (40ms latency)
- Language: English (`en`)
- Speed: 0.0 (normal)
- Emotion: `positivity:high` (friendly tone)

## Latency Optimization

Combined latency improvements:
- **STT (AssemblyAI)**: ~300ms
- **LLM (Azure GPT-4o-mini)**: ~150ms
- **TTS (Cartesia Sonic Turbo)**: ~40ms
- **Total pipeline**: ~490ms (vs ~600ms with Azure services)

## Pricing

- **AssemblyAI Universal Streaming**: $0.15 per hour
- **Cartesia TTS**: Check current pricing at cartesia.ai

## Switching Between Configurations

- **Azure STT/TTS**: Run `python agent.py` (default)
- **AssemblyAI STT + Cartesia TTS**: Run `python agent_assemblyai.py`

Both configurations use Azure OpenAI for the LLM component.