# Azure Services Setup Guide for LiveKit Agent

This guide will help you set up Azure services for STT, TTS, and LLM with your LiveKit agent.

## Prerequisites

1. Azure Account with active subscription
2. Azure CLI installed (optional but recommended)

## 1. Azure OpenAI Service Setup (for LLM)

### Create Azure OpenAI Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Azure OpenAI"
4. Click "Create"
5. Fill in:
   - Resource group: Create new or use existing
   - Region: Choose one that supports OpenAI (e.g., East US, West Europe)
   - Name: `your-openai-resource-name`
   - Pricing tier: Standard S0

### Deploy a Model

1. Go to your Azure OpenAI resource
2. Click on "Model deployments" → "Manage Deployments"
3. Click "Create new deployment"
4. Choose:
   - Model: `gpt-4o` (recommended) or `gpt-4o-mini` (faster/cheaper)
   - Deployment name: `gpt-4o-deployment`
   - Set appropriate rate limits

### Get Credentials

1. In your Azure OpenAI resource, go to "Keys and Endpoint"
2. Copy:
   - KEY 1 or KEY 2
   - Endpoint URL

## 2. Azure Speech Services Setup (for STT/TTS)

### Create Speech Service Resource

1. In Azure Portal, click "Create a resource"
2. Search for "Speech"
3. Select "Speech" by Microsoft
4. Click "Create"
5. Fill in:
   - Resource group: Same as OpenAI or create new
   - Region: Choose closest to your users
   - Name: `your-speech-resource-name`
   - Pricing tier: Standard S0 (or Free F0 for testing)

### Get Credentials

1. Go to your Speech resource
2. Click on "Keys and Endpoint"
3. Copy:
   - KEY 1 or KEY 2
   - Location/Region

## 3. Environment Variables

Add these to your `.env` file or GitHub Secrets:

```env
# Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-deployment

# Azure Speech Services
AZURE_SPEECH_KEY=your-speech-key
AZURE_SPEECH_REGION=eastus  # or your region

# Existing LiveKit credentials
LIVEKIT_URL=wss://your-instance.livekit.cloud
LIVEKIT_API_KEY=your-livekit-key
LIVEKIT_API_SECRET=your-livekit-secret
```

## 4. Update Your Agent

Replace your current `agent.py` with `agent_azure.py` or update the imports:

```python
from livekit.plugins import openai, azure, silero

# In your entrypoint function:
session = AgentSession(
    stt=azure.STT(language="en-US"),
    llm=openai.LLM.with_azure(
        model="gpt-4o",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_version="2024-02-01",
        temperature=0.7,
    ),
    tts=azure.TTS(voice="en-US-JennyNeural"),
    vad=silero.VAD.load(),
)
```

## 5. Available Voices for Azure TTS

Popular English voices:
- `en-US-JennyNeural` - Female, friendly
- `en-US-AriaNeural` - Female, professional
- `en-US-GuyNeural` - Male, conversational
- `en-US-JennyMultilingualNeural` - Supports multiple languages

Full list: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts

## 6. Cost Optimization Tips

1. **LLM**: Use `gpt-4o-mini` instead of `gpt-4o` for 10x cost savings
2. **TTS/STT**: Azure Speech has pay-per-use pricing
3. **Monitor usage**: Set up alerts in Azure Portal

## 7. Testing

1. Update `requirements.txt` and install:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the agent:
   ```bash
   python agent_azure.py dev
   ```

## 8. Troubleshooting

### "Resource not found" error
- Verify endpoint URL includes `https://` and trailing `/`
- Check deployment name matches exactly

### "Invalid API key" error
- Ensure you're using Azure OpenAI key, not regular OpenAI
- Check key hasn't expired or been regenerated

### Speech Services not working
- Verify region is correctly set (e.g., "eastus" not "East US")
- Ensure Speech resource is in a supported region

## 9. Performance Considerations

- **Latency**: Azure services add ~50-100ms vs direct APIs
- **Reliability**: Azure provides 99.9% SLA
- **Scalability**: No rate limits beyond your quota