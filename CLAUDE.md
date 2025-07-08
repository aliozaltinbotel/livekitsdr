# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Codebase Overview

This is a production-ready voice AI assistant built on LiveKit Cloud infrastructure. The system uses a Python agent backend with a Next.js frontend, designed for property rental management conversations.

## Architecture

### Backend (Python Agent)
- **Main Entry**: `agent/agent.py` - Voice assistant implementation
- **Key Classes**:
  - `CleanTTSWrapper`: Strips markdown formatting before TTS synthesis
  - `AssistantAgent`: Main agent logic with MCP integration
- **External Integrations**:
  - MCP Server (Model Context Protocol) for property data
  - AssemblyAI for STT, OpenAI for LLM, Cartesia for TTS

### Frontend (Next.js 15)
- **App Router** with TypeScript
- **LiveKit React Components** for real-time voice/video
- **Widget Mode** for embedding in external websites
- Component structure: `frontend/src/components/`

### MCP Server
- Separate microservice at `mcp_server/`
- Provides property management tools to the agent
- Runs on port 3001 in docker-compose setup

## Development Commands

### Setup
```bash
# First-time setup (creates venv, installs dependencies)
./setup.sh
```

### Running Locally
```bash
# Terminal 1: Python Agent
cd agent && source venv/bin/activate && python agent.py start

# Terminal 2: Frontend  
cd frontend && pnpm dev
```

### Frontend Commands
```bash
cd frontend
pnpm lint       # Run ESLint
pnpm build      # Production build
pnpm format     # Format with Prettier
```

### Running with Docker
```bash
docker-compose up --build
```

## Development Best Practices

- Always run python scripts via venv
- The agent automatically detects production mode via ENVIRONMENT variable
- MCP integration falls back to direct tool invocation if MCP server is unavailable
- Text responses are automatically chunked for optimal TTS delivery
- Markdown formatting is stripped before TTS to prevent speaking formatting characters

## Key Configuration

### Environment Variables
- **Agent**: See `agent/.env.example` for required vars (LiveKit, AI services)
- **Frontend**: See `frontend/.env.example` for LiveKit connection
- **MCP Server**: Uses `mcp_server/.env` for property data configuration

### Agent Configuration
- STT: AssemblyAI Universal (2-channel for better accuracy)
- LLM: OpenAI GPT-4o-mini with Azure fallback
- TTS: Cartesia Sonic-Turbo
- VAD: Silero for voice activity detection

## Testing Approach

### Frontend
- Component testing with React Testing Library
- E2E testing considerations for LiveKit components

### Agent
- Unit tests with pytest for agent logic
- Mock LiveKit SDK for testing conversation flows
- Test MCP integration with mock server

### Running Tests
```bash
# Frontend tests
cd frontend && pnpm test

# Agent tests  
cd agent && source venv/bin/activate && pytest
```

## Architecture Notes

1. **Text Processing Pipeline**: User speech → STT → LLM → Markdown stripping → Text chunking → TTS
2. **MCP Integration**: Agent discovers tools via MCP protocol, allowing dynamic capability expansion
3. **Response Caching**: Built-in caching for frequently asked questions
4. **Interruption Handling**: Min 2-word utterances to prevent false interruptions
5. **Widget Mode**: Frontend can be embedded via iframe with query parameters for customization