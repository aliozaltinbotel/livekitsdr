# Latency Optimization Analysis for LiveKit SDR

## Current Setup ✅

**Great news!** Your services are optimally configured for low latency:

- **LiveKit Cloud Region**: US East
- **Azure Services Region**: East US (eastus)
- **Status**: Both services are in the same region! 🎯

## Latency Breakdown

### Current Architecture
```
User → LiveKit Cloud (US East) → Your Agent (Azure East US) → LiveKit Cloud → User
```

### Typical Latency Components

1. **User to LiveKit Cloud**: 10-50ms (depends on user location)
2. **LiveKit to Azure Agent**: ~5-15ms (same region)
3. **Azure Processing**:
   - STT (Speech-to-Text): ~100-200ms
   - LLM (GPT-4o): ~300-500ms
   - TTS (Text-to-Speech): ~100-200ms
4. **Total Round Trip**: ~600-1000ms

## Optimization Strategies

### 1. ✅ Already Implemented
- [x] LiveKit and Azure in same region (US East)
- [x] Using Azure's high-performance models
- [x] Voice Activity Detection (VAD) for efficient processing

### 2. Further Optimizations

#### a) **Model Selection**
- Consider using `gpt-4o-mini` instead of `gpt-4o` for 2-3x faster responses
- Trade-off: Slightly less capable but much faster

#### b) **Streaming Responses**
- Enable streaming from LLM to TTS to reduce perceived latency
- User hears the beginning of response while rest is being generated

#### c) **Turn Detection Tuning**
```python
# In agent.py, adjust VAD settings
vad=silero.VAD.load(
    min_speech_duration=0.1,  # Faster detection
    min_silence_duration=0.3,  # Quicker turn-taking
)
```

#### d) **Connection Pooling**
- Pre-warm connections to Azure services
- Reduces cold start latency

## Measuring Real Latency

### From Container Logs
You can measure actual latency by checking timestamps in your container logs:
```bash
az container logs --resource-group livekitsdr-rg --name livekitsdr-agent-container | grep -E "(User:|Agent:)" | tail -20
```

### Key Metrics to Monitor
1. **Speech Detection Latency**: Time from user speaking to STT result
2. **Response Generation**: Time from STT complete to TTS start
3. **First Byte Latency**: Time until user hears first audio

## Regional Deployment Strategy

If you have users in other regions, consider:

1. **Multi-Region Deployment**:
   - Deploy agents in multiple Azure regions
   - LiveKit Cloud can route to nearest agent

2. **LiveKit Cloud Regions**:
   - US East (current) ✅
   - US West
   - Europe
   - Asia Pacific

3. **Request Additional Regions**:
   Contact LiveKit support to add presence in specific regions

## Performance Benchmarks

### Current Expected Performance
- **Excellent**: <800ms total latency (same region users)
- **Good**: 800-1200ms (cross-region users)
- **Acceptable**: 1200-1500ms (international users)

### Your Current Setup
With both services in US East:
- **Local users (East US)**: ~600-800ms ✅
- **West Coast users**: ~700-1000ms
- **European users**: ~900-1300ms
- **Asian users**: ~1000-1500ms

## Recommendations

1. **Keep current setup** - You have optimal regional alignment
2. **Monitor actual latencies** using container logs
3. **Consider gpt-4o-mini** if faster responses needed
4. **Enable response streaming** when LiveKit agents support it
5. **Add European deployment** if you have significant EU traffic

## Testing Latency

To test real-world latency:
1. Join a session from different locations
2. Measure time between speaking and hearing response
3. Check container logs for processing times
4. Use browser dev tools to measure WebRTC statistics