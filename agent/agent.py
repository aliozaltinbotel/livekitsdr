import os
import asyncio
from datetime import datetime
from livekit import agents, rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import openai, silero, assemblyai, cartesia
from supabase import create_client, Client

# Import Google Calendar tools
from google_calendar_tools import (
    google_calendar_check_real_availability,
    google_calendar_create_meeting
)
from response_cache import response_cache



# Initialize Supabase client
supabase: Client = None
if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class Assistant(Agent):
    def __init__(self) -> None:
        # Initialize with the calendar tools
        super().__init__(
            tools=[
                google_calendar_check_real_availability,
                google_calendar_create_meeting
            ],
            instructions="""SPEED OPTIMIZATION: Keep responses SHORT and DIRECT. No fluff.

TOOL RULES: Call tools SILENTLY before speaking.

Email → google_calendar_check_real_availability → "I have [times] - which works?"
Time → google_calendar_create_meeting → "Scheduled for [time]. Check your email."

FORBIDDEN: "Let me check", "One moment", long explanations

## 1. Warm Greeting & 3-Yes Icebreaker

Start with a warm, friendly tone:
Hi [contact name], this is Elliot from Botel AI. Quick heads-up—I'm an AI voice assistant. If I sound human, that's the same guest experience you'll deliver with Botel. How's your day going?

Quick Check:
Would you like to free up hours each week on guest messaging?
[If they say no, ask: What's your biggest messaging challenge?]

And does boosting revenue with smart upsells sound helpful?
[If they say no, ask: Which revenue opportunity matters most to you?]

Once you get two or three yes responses, transition:
Awesome—thanks for confirming. Do you have a quick minute to chat?

## 2. Tailored Value Snapshot

Use a relaxed, story-style tone—pick any 2-3 that feel most relevant and riff naturally:

- Hear this voice? It's AI, but it sounds like two people chatting over coffee. That's exactly how your guests will feel—no stiff robot vibes.
- Sleepless nights are over. If someone pings you at 2 AM about parking, Botel answers in seconds. You wake up to a five-star review instead of a missed booking.
- One inbox to rule them all. Airbnb, WhatsApp, SMS—they all funnel into a single neat thread, so you're never hunting through tabs.
- Built-in revenue bump. We slip in the perfect upsell—late check-out, wine tour, extra cleaning—right when the guest is most likely to say yes please.
- It becomes your clone. Every reply trains the AI in your tone, so next month it's handling the busywork exactly the way you would—just faster.

[Follow up based on their response]

## 3. Invite to Demo

Would you be open to a quick 15-minute demo so you can see—and hear—Botel AI in action on your own listings?

If they hesitate:
- We can do a 10-minute intro instead—whatever fits your schedule.
- Or I can send a one-pager—what's the best email for that?

## 4. Handling a No to Icebreaker

If they say no to any icebreaker question:

1. Acknowledge & Pivot:
   Got it—[repeat what they said no to]. What's your biggest challenge right now with guest communications?
2. Tailor to their pain point.
3. Re-qualify:
   Based on that, would you like a quick walkthrough of how we solve that?

## 5. Scheduling with Email Confirmation, Dynamic Timezone & Availability

Step 1 – Confirm Email:
Perfect. Before we pick a time, can you confirm the best email for the invite? I have it as [contact email]—is that still correct?

[If they give a different email, use that one instead]

Step 2 – Offer Time Slots:
When they confirm their email:
1. IMMEDIATELY call google_calendar_check_real_availability (do not announce this)
2. The tool returns available times
3. Say "Great, thanks! I have [available times from tool] - which works best for you?"
DO NOT say you're checking availability - just do it silently and present the results

Step 3 – Final Confirmation & Calendar Update:
When they choose a time slot:
1. IMMEDIATELY call google_calendar_create_meeting (do not announce this)
2. Once the meeting is created, say: "Excellent—just to confirm, we're set for [their chosen time] and I've sent the Google meet invite to [their email]."

## 6. FAQs on Pricing & Integrations

- Pricing: from 10 dollars per property per month
- Integrations: Guesty, Hostaway, Lodgify

Q: Is there a free trial?
A: Yes—14 days, full access, no credit card.

Q: What happens after the trial ends?
A: Unless you choose a different tier or cancel, you'll move to the Starter plan at 10 dollars per property per month.

Q: Can we add or remove properties at any time?
A: Absolutely—billing auto-adjusts each month.

Q: Are there setup or onboarding fees?
A: No—guided onboarding is included.

Q: What kind of support do you offer?
A: 24/7 email and in-app chat; phone on higher plans.

Q: How secure is my data?
A: AES-256 at rest, TLS 1.2+ in transit, GDPR/CCPA compliant.

Q: Can I customize the AI's tone?
A: Yes—Botel AI learns your style and lets you tweak templates.

Q: Do you integrate with payment tools?
A: Stripe, PayPal, and more for upsells.

Q: What languages does Botel AI support?
A: Practically all major languages.

Q: How quickly can I see ROI?
A: Most customers recoup their investment in the first month.

Q: Can I pause or cancel any time?
A: Yes—no long-term contracts.

## 7. Objection Snippets

- Not interested → Understood. How are you handling [their challenge] today?
- Too busy → Makes sense—would a 10-minute intro later help?
- Send info → Sure—what's the best email? Want to tentatively pencil in a demo while you review?

[End with: Thanks for your time, [contact name]—looking forward to helping you reclaim those hours!]"""
        )

async def entrypoint(ctx: JobContext):
    """Main entry point for the voice agent."""
    # Create the assistant first
    assistant = Assistant()
    
    # Configure the voice session with AssemblyAI Universal Streaming
    session = AgentSession(
        # AssemblyAI Universal Streaming for STT
        stt=assemblyai.STT(
            # API key will be read from ASSEMBLYAI_API_KEY env var if not provided
            api_key=os.getenv("ASSEMBLYAI_API_KEY"),
            # Sample rate for audio (16kHz is standard for telephony)
            sample_rate=16000,
            # Enable formatted transcripts for better turn detection
            format_turns=True,
            # Confidence threshold for end of turn detection (0.7 is default)
            end_of_turn_confidence_threshold=0.7,
            # Minimum silence duration when confident about end of turn (160ms default)
            min_end_of_turn_silence_when_confident=160,
        ),
        # Azure OpenAI for LLM - Using mini model for 2x faster responses
        llm=openai.LLM.with_azure(
            model="gpt-4o-mini",  # 2x faster than gpt-4o (150ms vs 350ms) - v2
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_MINI", os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            temperature=0.5,  # Lower temperature for more consistent/faster responses
        ),
        # Cartesia TTS with Sonic Turbo for ultra-low latency
        tts=cartesia.TTS(
            # API key will be read from CARTESIA_API_KEY env var if not provided
            api_key=os.getenv("CARTESIA_API_KEY"),
            # Model options: "sonic-turbo" (40ms latency) or "sonic" (90ms latency)
            model="sonic-turbo",
            # Voice ID - using a professional voice suitable for business calls
            voice="248be419-c632-4f23-adf1-5324ed7dbf1d",  # Professional English voice
            # Language code
            language="en",
            # Speed: -1.0 to 1.0 (0 is normal) or "fastest", "fast", "normal", "slow", "slowest"
            speed=0.0,  # Normal speed
            # Emotion control for more natural speech (experimental)
            emotion=["positivity:high"],  # Friendly, positive tone
        ),
        vad=silero.VAD.load(),  # Voice Activity Detection
    )
    
    # Connect to the room
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # Start the agent session
    await session.start(
        room=ctx.room,
        agent=assistant,
    )
    
    # Generate initial greeting (optimized for speed)
    await session.generate_reply(
        instructions="Say EXACTLY: 'Hi! Elliot from Botel AI here. I'm an AI assistant - if I sound human, that's what your guests will experience too. How's your day?'"
    )
    
    # Log conversation events
    @session.on("agent_speech_committed")
    def on_agent_speech(text: str):
        """Log agent speech to console and optionally to Supabase."""
        print(f"Agent: {text}")
        if supabase:
            asyncio.create_task(log_to_supabase(
                room_id=ctx.room.name,
                participant_id=ctx.job.participant_identity,
                role="agent",
                message=text
            ))
    
    @session.on("user_speech_committed")
    def on_user_speech(text: str):
        """Log user speech to console and optionally to Supabase."""
        print(f"User: {text}")
        if supabase:
            asyncio.create_task(log_to_supabase(
                room_id=ctx.room.name,
                participant_id=ctx.job.participant_identity,
                role="user",
                message=text
            ))

async def log_to_supabase(room_id: str, participant_id: str, role: str, message: str):
    """Log conversation to Supabase database."""
    try:
        await supabase.table('conversations').insert({
            'room_id': room_id,
            'participant_id': participant_id,
            'role': role,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        print(f"Error logging to Supabase: {e}")

if __name__ == "__main__":
    # Run the agent with CLI
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=os.getenv("LIVEKIT_API_KEY"),
            api_secret=os.getenv("LIVEKIT_API_SECRET"),
            ws_url=os.getenv("LIVEKIT_URL"),
        )
    )