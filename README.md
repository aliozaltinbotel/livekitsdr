# LiveKit Voice Assistant

A production-ready voice AI agent built with LiveKit Cloud, featuring real-time speech recognition, natural language processing, and text-to-speech capabilities.

## 🏗️ Architecture

- **Frontend**: Next.js 15 with LiveKit React Components
- **Backend**: Python agent with LiveKit Agents SDK
- **Infrastructure**: LiveKit Cloud (managed WebRTC)
- **AI Stack**:
  - STT: AssemblyAI Universal
  - LLM: OpenAI GPT-4o-mini
  - TTS: Cartesia Sonic-Turbo
- **Database**: Supabase (optional, for conversation logging)

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and pnpm
- Python 3.9+
- LiveKit Cloud account
- API keys for OpenAI, AssemblyAI, and Cartesia

### Setup

1. **Clone and configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

2. **Run automated setup:**
   ```bash
   ./setup.sh
   ```

3. **Start the services:**

   Terminal 1 - Python Agent:
   ```bash
   cd agent
   source venv/bin/activate
   python agent.py start
   ```

   Terminal 2 - Next.js Frontend:
   ```bash
   cd frontend
   pnpm dev
   ```

4. **Open http://localhost:3000**

## 📁 Project Structure

```
livekitsdr/
├── frontend/          # Next.js web interface
│   ├── app/          # App router pages
│   ├── components/   # React components
│   └── lib/          # Utilities
├── agent/            # Python voice agent
│   ├── agent.py      # Main agent logic
│   └── requirements.txt
```

## 🔧 Configuration

### Environment Variables

```env
# LiveKit Cloud
LIVEKIT_URL=wss://<your-project>.livekit.cloud
LIVEKIT_API_KEY=<your-api-key>
LIVEKIT_API_SECRET=<your-api-secret>

# AI Services
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
CARTESIA_API_KEY=...
```

### Agent Configuration

The agent is configured with:
- VAD (Voice Activity Detection) with Silero
- Multilingual turn detection
- Interruption handling (min 2 words)
- Comprehensive conversation logging

## 🎮 Features

- **Real-time voice interaction** with <200ms latency
- **Natural conversation flow** with interruption handling
- **Multilingual support** with automatic language detection
- **Conversation history** with comprehensive logging
- **Noise cancellation** and echo reduction
- `call_summaries` - Aggregated view

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

### Agent (Cloud/Docker)
```bash
cd agent
docker build -t voice-agent .
docker run --env-file .env voice-agent
```

## 🛠️ Development

### Adding Custom Features

1. **Modify agent behavior**: Edit `agent/agent.py`
2. **Update UI**: Modify components in `frontend/components/`
3. **Add new AI capabilities**: Update the pipeline configuration

### Testing

```bash
# Frontend
cd frontend && pnpm lint

# Agent
cd agent && python -m pytest
```

## 📚 Resources

- [LiveKit Docs](https://docs.livekit.io)
- [LiveKit Agents](https://docs.livekit.io/agents/)
- [Voice Assistant Template](https://github.com/livekit-examples/voice-assistant-frontend)

## 📄 License

MIT