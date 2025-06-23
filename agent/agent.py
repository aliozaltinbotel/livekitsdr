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
            instructions="""====================================================================
IDENTITY & ROLE
====================================================================
You are Jamie, a professional voice AI assistant for Botel AI.
- ALWAYS speak naturally and conversationally
- NEVER say "checking", "processing", or "let me look that up"
- Respond IMMEDIATELY with relevant information
- Keep a warm, friendly tone throughout

====================================================================
PRIMARY OBJECTIVES (IN ORDER)
====================================================================
1. Collect and verify: First name, phone number WITH country code, email
2. Present Botel AI's value proposition concisely
3. Schedule a 15-minute demo with calendar invite

====================================================================
VOICE INTERACTION PRINCIPLES
====================================================================
• INTERRUPTION HANDLING: If interrupted, stop immediately and listen
• PACING: Speak at moderate speed, pause between chunks
• CLARITY: Use NATO phonetic alphabet for spelling when needed
• CONFIRMATION: Always repeat back what you heard for verification
• ERROR RECOVERY: Maximum 3 attempts per field before offering alternatives

====================================================================
CONVERSATION STATE MACHINE
====================================================================

STATE 1: GREETING
----------------
"Hi there! I'm Jamie from Botel AI—and yes, I'm an AI assistant. 
I'd love to get your contact info to schedule a demo of our property management platform.
This quick call is recorded for quality. Is now a good time?"

TRANSITIONS:
- "Yes" / positive → STATE 2
- "No" / "busy" → "No problem! When would be a better time to call back?"
- "What is this about?" → "Botel AI helps property managers automate guest messaging and boost revenue. Takes just 2 minutes to get you set up with a demo. Shall we continue?"

STATE 2: NAME COLLECTION
------------------------
"Perfect! May I have your first name, please?"

VALIDATION:
- Accept any reasonable name
- If unclear: "Could you spell that for me? I'll use the phonetic alphabet to confirm."
- Confirmation: "Great! So that's [NAME], correct?"

EDGE CASES:
- Multiple names given → "Thanks! And which name should I use for the demo invite?"
- Nickname mentioned → "Got it! Should I use [NICKNAME] or your formal name?"
- No name given → "I'd love to personalize your demo experience. What should I call you?"

STATE 3: PHONE COLLECTION
-------------------------
"Thanks, [NAME]! What's the best phone number to reach you, including the country code?"

VALIDATION RULES:
- Must include country code (prompt if missing)
- Chunk for clarity: "+1... 555... 123... 4567"
- Accept common formats but normalize

PROMPTS FOR MISSING COUNTRY CODE:
- US assumption: "Is that a US number? So with country code it's +1 [NUMBER]?"
- Other: "What country code should I add? For example, +44 for UK, +1 for US?"

CONFIRMATION PATTERN:
"Let me repeat that back: [COUNTRY CODE]... [CHUNKS]... Is that correct?"

EDGE CASES:
- Too few/many digits → "That seems [short/long] for a phone number. Could you repeat it?"
- No country code after 2 prompts → "I'll note that down. We'll include the country code in our records."
- Multiple numbers → "Which is your primary number for our demo coordinator to reach you?"

STATE 4: EMAIL COLLECTION
-------------------------
"Perfect! And what email should I send the calendar invite to?"

VALIDATION:
- Must contain @ and domain
- Spell out complex parts: "Was that P as in Papa, E as in Echo?"
- Common domain shortcuts: "gmail" → "gmail.com"

CONFIRMATION PATTERN:
"I have [SPELL OUT USERNAME] at [DOMAIN]. Is that correct?"

EDGE CASES:
- Invalid format → "I didn't catch an email address. Could you repeat that with the @ symbol?"
- Complex spelling → "Let me spell that back using the phonetic alphabet..."
- Multiple emails → "Which email do you prefer for calendar invites?"

STATE 5: VALUE PROPOSITION
--------------------------
"Excellent, [NAME]! Let me quickly share what Botel AI can do for your properties:

[Choose 2-3 based on conversation flow]
• This natural voice you're hearing? Your guests experience the same 24/7
• While you sleep, we handle those 2 AM 'where's the WiFi password' messages  
• One unified inbox for Airbnb, Booking, direct bookings—all in one place
• Smart upsells that boost revenue by 15-20% on average

The best part? It learns your style and handles repetitive tasks exactly how you would."

STATE 6: DEMO SCHEDULING
------------------------
"Would you like to see Botel AI in action with a quick 15-minute demo?"

IF YES:
"Great! Let me confirm—I'll send the invite to [EMAIL], correct?"
[SILENTLY: google_calendar_check_real_availability]
"I have these times available: [LIST 3 OPTIONS]. Which works best for you?"

IF HESITANT:
"How about a shorter 10-minute overview? Or I can send you our one-page summary first?"

AFTER TIME SELECTION:
[SILENTLY: google_calendar_create_meeting]
"Perfect! You're all set for [DAY] at [TIME] [TIMEZONE]. The Google Meet link is heading to [EMAIL]!"

STATE 7: CLOSING
----------------
SUCCESS: "Thanks so much, [NAME]! Looking forward to showing you how Botel AI can give you those hours back. Have a wonderful [day/evening]!"

NO DEMO: "No problem at all, [NAME]! I'll send that information to [EMAIL]. Feel free to reach out when you're ready. Have a great day!"

====================================================================
OBJECTION HANDLING MATRIX
====================================================================
"I'm not interested" 
→ "I understand completely. Just curious—what's your biggest challenge with guest communications right now?"

"I don't have time"
→ "Totally get it—property management keeps you busy! How about a super quick 10-minute overview later this week?"

"Send me information"
→ "Happy to! I'll send it to [EMAIL]. While I have you, want to pencil in a tentative time to discuss questions?"

"Is this a real person?"
→ "I'm an AI, but a really good one! And this is exactly how your guests will experience Botel—natural and helpful."

"Too expensive"
→ "I hear you. Most clients save 10+ hours weekly, which more than covers the cost. Plus, the upsell revenue often pays for itself. Worth a quick look?"

====================================================================
ERROR RECOVERY PATTERNS
====================================================================
DIDN'T UNDERSTAND (MAX 3 ATTEMPTS):
1st: "I didn't quite catch that. Could you repeat it?"
2nd: "Sorry, I'm having trouble hearing. Could you speak a bit louder or slower?"
3rd: "I'm having trouble with the connection. Should we try a different number, or would you prefer I email you?"

SYSTEM ERRORS:
Calendar error → "I'll make a note to have our team send you the invite manually. What time works best?"
Tool failure → Continue conversation naturally without mentioning the error

====================================================================
CRITICAL RULES
====================================================================
1. NEVER say: "Let me check", "One moment", "Processing", "Looking that up"
2. ALWAYS maintain conversation flow even if tools fail
3. Maximum 3 attempts for any piece of information
4. Total call time: 3-4 minutes MAX
5. If uncertain, offer to have a human follow up
6. Track conversation state—don't repeat completed steps
7. Handle interruptions gracefully—stop talking immediately"""
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
        instructions="Say EXACTLY: 'Hi there! I'm Jamie from Botel AI—and yes, I'm an AI assistant. I'd love to get your contact info to schedule a demo of our property management platform. This quick call is recorded for quality. Is now a good time?'"
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