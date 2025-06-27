# LiveKit + LangChain Integration Plan for BotelLLM

## Current Architecture Analysis

### BotelLLM Application
- **Framework**: FastAPI + LangChain
- **LLM Provider**: Azure OpenAI (gpt-4.1-mini)
- **Agent System**: LangChain agents with multiple tools
- **Key Features**:
  - Conversation processing with agent-based workflow
  - PMS integration for property data
  - Multiple specialized services (upsell, reviews, gap nights)
  - Tool-based architecture for different capabilities
  - Tracing with LangSmith

### LiveKit Voice Agent
- **Framework**: LiveKit Agents SDK
- **Voice Pipeline**: STT → LLM → TTS
- **Current Tools**: MCP-based property context and availability checking

## Integration Approaches

### Option 1: Unified Agent Architecture (Recommended)
Create a single LiveKit agent that uses your existing LangChain agents as the brain.

```python
# livekit_langchain_agent.py
import os
from livekit import agents, rtc
from livekit.agents import llm, AutoSubscribe, JobContext, AgentSession
from typing import Dict, Any
import aiohttp
import json

class LangChainVoiceAgent:
    def __init__(self, botelllm_url: str = "http://localhost:80"):
        self.botelllm_url = botelllm_url
        self.session = None
        
    async def process_with_langchain(self, 
                                   messages: list, 
                                   context: Dict[str, Any]) -> str:
        """Send conversation to BotelLLM and get response"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        payload = {
            "messages": messages,
            "propertyId": context.get("property_id"),
            "customerId": context.get("customer_id"),
            "reservationId": context.get("reservation_id"),
            # Add other context as needed
        }
        
        async with self.session.post(
            f"{self.botelllm_url}/llm/conversations/",
            json=payload
        ) as response:
            result = await response.json()
            return result.get("response", "I'm processing your request...")

# Custom LLM wrapper for LangChain
class LangChainLLM(llm.LLM):
    def __init__(self, agent: LangChainVoiceAgent):
        super().__init__()
        self.agent = agent
        self.conversation_history = []
        
    async def chat(self, messages: list[llm.ChatMessage]) -> llm.ChatResponse:
        # Convert LiveKit messages to LangChain format
        langchain_messages = []
        for msg in messages:
            langchain_messages.append({
                "role": msg.role,
                "content": msg.content
            })
            
        # Get response from LangChain agent
        response = await self.agent.process_with_langchain(
            langchain_messages,
            context={}  # Add room context here
        )
        
        return llm.ChatResponse(
            choices=[llm.Choice(
                message=llm.ChatMessage(role="assistant", content=response)
            )]
        )
```

### Option 2: Parallel Services Architecture
Keep both services separate but connected through shared state.

```python
# Architecture:
# User → LiveKit Agent → Voice Processing → Send to LangChain
#                                        ↓
# User ← LiveKit Agent ← Voice Response ← LangChain Response

# Shared Redis/Database for:
# - Conversation history
# - User context
# - Property/reservation data
```

### Option 3: Tool-Based Integration
Add voice tools to your existing LangChain agents.

```python
# Add to your LangChain tools
from langchain.tools import Tool

voice_tools = [
    Tool(
        name="start_voice_call",
        description="Start a voice conversation with the user",
        func=self._start_livekit_room
    ),
    Tool(
        name="transcribe_voice",
        description="Transcribe user's voice input",
        func=self._transcribe_audio
    ),
    Tool(
        name="speak_response",
        description="Convert text to speech for the user",
        func=self._text_to_speech
    )
]
```

## Implementation Steps

### Phase 1: Basic Integration (Week 1)
1. **Create LiveKit wrapper for LangChain**
   ```python
   # botelllm/src/services/livekit_service.py
   class LiveKitService:
       def __init__(self):
           self.rooms = {}
           
       async def create_voice_session(self, user_id: str):
           # Create LiveKit room
           # Start voice agent
           # Return room URL
   ```

2. **Add voice endpoints to FastAPI**
   ```python
   # botelllm/main.py
   from src.routes.voice_route import voice_router
   
   app.include_router(
       voice_router,
       prefix="/llm/voice",
   )
   ```

3. **Create hybrid agent**
   ```python
   # botelllm/src/agents/voice_agent.py
   class VoiceLangChainAgent:
       def __init__(self):
           self.langchain_agent = ConversationAgentService()
           self.voice_pipeline = self._setup_voice_pipeline()
   ```

### Phase 2: Advanced Features (Week 2-3)
1. **Context Preservation**
   - Share conversation history between voice and text
   - Maintain user context across channels
   - Sync property/reservation data

2. **Tool Integration**
   - Enable LangChain tools in voice conversations
   - Add voice-specific tools (pause, transfer, etc.)
   - Implement tool result vocalization

3. **Multi-modal Responses**
   - Send visual data during voice calls
   - Share documents/images
   - Display booking confirmations

### Phase 3: Production Optimization (Week 4)
1. **Performance**
   - Implement response streaming
   - Optimize latency
   - Add caching layer

2. **Monitoring**
   - Unified logging
   - Voice quality metrics
   - Conversation analytics

## Technical Requirements

### Dependencies to Add
```txt
# Add to requirements.txt
livekit==0.11.1
livekit-agents==0.8.0
livekit-plugins-openai==0.7.0
livekit-plugins-deepgram==0.6.0
redis==5.0.0  # For shared state
```

### Environment Variables
```env
# LiveKit
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# Voice Services
DEEPGRAM_API_KEY=your-deepgram-key
ELEVENLABS_API_KEY=your-elevenlabs-key
```

### Docker Compose Update
```yaml
version: '3.8'
services:
  botelllm:
    build: ./botelllm
    ports:
      - "80:80"
    environment:
      - LIVEKIT_ENABLED=true
    
  livekit-agent:
    build: ./livekit-agent
    depends_on:
      - botelllm
    environment:
      - BOTELLLM_URL=http://botelllm:80
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Code Example: Minimal Integration

```python
# botelllm/src/services/voice_langchain_service.py
from typing import Dict, Any, List
from langchain.schema import HumanMessage, AIMessage
from livekit.agents import llm as livekit_llm
import json

class VoiceLangChainService:
    """Bridge between LiveKit voice and LangChain agents"""
    
    def __init__(self, conversation_agent: ConversationAgentService):
        self.agent = conversation_agent
        self.active_sessions: Dict[str, Any] = {}
        
    async def process_voice_input(self, 
                                 room_id: str,
                                 user_message: str,
                                 context: Dict[str, Any]) -> str:
        """Process voice input through LangChain agent"""
        
        # Get or create session
        session = self.active_sessions.get(room_id, {
            "messages": [],
            "context": context
        })
        
        # Add user message
        session["messages"].append(HumanMessage(content=user_message))
        
        # Process through LangChain agent
        result = await self.agent.process_conversation(
            messages=session["messages"],
            property_id=context.get("property_id"),
            customer_id=context.get("customer_id"),
            channel="voice",
            metadata={
                "room_id": room_id,
                "voice_session": True
            }
        )
        
        # Add AI response to history
        session["messages"].append(AIMessage(content=result.response))
        
        # Update session
        self.active_sessions[room_id] = session
        
        return result.response
        
    async def get_voice_tools(self) -> List[livekit_llm.FunctionTool]:
        """Convert LangChain tools to LiveKit function tools"""
        voice_tools = []
        
        for tool in self.agent.tools:
            # Create LiveKit-compatible tool
            async def tool_wrapper(arguments: str):
                args = json.loads(arguments)
                result = await tool.arun(**args)
                return json.dumps({"result": result})
                
            voice_tool = livekit_llm.FunctionTool(
                name=tool.name,
                description=tool.description,
                parameters={
                    "type": "object",
                    "properties": {},  # Define based on tool
                },
                function=tool_wrapper
            )
            voice_tools.append(voice_tool)
            
        return voice_tools
```

## Benefits of Integration

1. **Unified Intelligence**: Single source of truth for all AI logic
2. **Consistent Responses**: Same agent handles voice and text
3. **Shared Context**: Conversation history across channels
4. **Tool Reuse**: All LangChain tools available in voice
5. **Easier Maintenance**: One codebase for AI logic

## Next Steps

1. **Proof of Concept**:
   - Create minimal integration
   - Test with simple conversation flow
   - Measure latency impact

2. **Architecture Decision**:
   - Choose integration approach
   - Design state management
   - Plan deployment strategy

3. **Implementation**:
   - Start with Phase 1
   - Iterate based on feedback
   - Scale to production

## Considerations

- **Latency**: Additional hop to LangChain may add 100-200ms
- **Streaming**: LangChain responses need to be streamed for voice
- **Error Handling**: Voice requires graceful fallbacks
- **Context Size**: Voice conversations can be longer
- **Cost**: Voice interactions use more tokens

This integration would give you a powerful voice-enabled LangChain application that maintains all your existing business logic while adding natural voice interactions!