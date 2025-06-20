# Streaming Response Implementation TODO

## Current Status
LiveKit Agents framework currently processes responses in a pipeline:
1. STT completes → 2. LLM generates full response → 3. TTS starts

## Streaming Architecture (Future Implementation)
```
STT → LLM (streaming) → TTS (streaming) → User hears first words quickly
         ↓                    ↓
    Partial text         Start speaking
    chunks arrive        immediately
```

## Implementation Notes

### Option 1: LLM Streaming to TTS
```python
# Future implementation when LiveKit supports it
llm=openai.LLM.with_azure(
    model="gpt-4o-mini",
    stream=True,  # Enable streaming
    stream_callback=lambda text: tts.queue_partial(text)
)
```

### Option 2: Sentence-Level Streaming
- Break LLM response into sentences
- Send each sentence to TTS immediately
- User hears first sentence while rest generates

### Option 3: Token-Level Streaming
- Stream individual tokens from LLM
- Buffer until punctuation
- Send complete phrases to TTS

## Current Workaround
For now, we've optimized by:
1. Using faster model (gpt-4o-mini)
2. Shorter prompts
3. Response caching
4. Lower temperature for consistency

## Monitor LiveKit Updates
Check LiveKit Agents releases for streaming support:
- https://github.com/livekit/agents/releases
- https://docs.livekit.io/agents/

When streaming is available, it will reduce perceived latency by 200-300ms!