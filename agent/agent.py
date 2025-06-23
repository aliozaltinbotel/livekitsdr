import os
import asyncio
from datetime import datetime
from livekit import agents, rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import openai, silero, assemblyai, cartesia

# Import Google Calendar tools
from google_calendar_tools import (
    google_calendar_check_real_availability,
    google_calendar_create_meeting
)
from response_cache import response_cache
from supabase_logger import supabase_logger

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
- NEVER remain silent for more than 5 seconds
- If user stops talking, wait 5 seconds then gently prompt to continue

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
• SILENCE HANDLING: After 5 seconds of silence, gently prompt to continue
• PACING: Speak at moderate speed, pause between chunks
• CLARITY: Use NATO phonetic alphabet for spelling when needed
• CONFIRMATION: Always repeat back what you heard for verification
• ERROR RECOVERY: Maximum 3 attempts per field before offering alternatives

SILENCE RECOVERY PROMPTS (use after 5 seconds of no response):
- First silence: "Are you still there?"
- Second silence: "I'm here when you're ready to continue."
- Third silence: "Would you like me to repeat the question?"
- During data collection: "Take your time. Just let me know when you're ready."
- After question: "Did you need me to clarify anything?"

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

SILENCE HANDLING:
- After 5 seconds: "Take your time. What's your first name?"
- After 10 seconds: "Are you still there? I just need your first name to continue."

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
"Great! Let me confirm—I'll send the invite to {USE THE ACTUAL EMAIL YOU COLLECTED}, correct?"
[SILENTLY: Call google_calendar_check_real_availability with timezone parameter]
"I have these times available: {USE THE ACTUAL TIMES RETURNED BY THE TOOL}. Which works best for you?"

IF HESITANT:
"How about a shorter 10-minute overview? Or I can send you our one-page summary first?"

AFTER TIME SELECTION:
[SILENTLY: Call google_calendar_create_meeting with:
  - email: THE ACTUAL EMAIL ADDRESS YOU COLLECTED (not "[email]" or placeholder)
  - meeting_time: THE EXACT TIME THE USER SELECTED
  - timezone: "America/New_York" or user's timezone if mentioned]
"Perfect! You're all set for {THE ACTUAL TIME SELECTED}. The Google Meet link is heading to {THE ACTUAL EMAIL}!"

CRITICAL: When calling tools, use the ACTUAL values collected from the user, not placeholders!

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
7. Handle interruptions gracefully—stop talking immediately
8. SILENCE CONTINUATION: After 5 seconds of silence, ALWAYS prompt to continue
9. NEVER go completely silent—keep the conversation alive with gentle prompts

====================================================================
VARIABLE USAGE - EXTREMELY IMPORTANT
====================================================================
When you collect information from the user, you MUST:
1. Store the ACTUAL values they provide (name, email, phone)
2. Use these ACTUAL values when calling functions
3. NEVER use placeholders like "[email]", "[name]", "[contact email]"
4. When calling google_calendar_create_meeting, pass the REAL email address

Example:
- User says: "My email is john@example.com"
- You store: john@example.com
- When calling tool: email="john@example.com" (NOT email="[email]")

====================================================================
SILENCE HANDLING - CRITICAL FOR NATURAL CONVERSATION
====================================================================
When the user goes silent, you MUST continue the conversation:

AFTER ASKING A QUESTION (5 second silence):
- First prompt: "Are you still there?"
- Second prompt: "I'm here whenever you're ready."
- Third prompt: "Would you like me to repeat the question?"

DURING DATA ENTRY (5 second silence):
- "Take your time, I'm listening."
- "No rush, just let me know when you're ready."

AFTER INTERRUPTION (5 second silence):
- "Sorry, please go ahead."
- "I'm listening, what were you saying?"

MID-CONVERSATION (5 second silence):
- "Is everything okay on your end?"
- "Can you hear me alright?"

TECHNICAL ISSUES (10 second silence):
- "It seems we might have a connection issue. Can you hear me?"
- "If you're having trouble hearing me, please let me know."

REMEMBER: A voice conversation should NEVER have long silences. Keep it flowing!"""
        )

async def entrypoint(ctx: JobContext):
    """Main entry point for the voice agent."""
    # Start Supabase session logging
    room_name = getattr(ctx.room, 'name', None) or ctx.job.id
    session_id = await supabase_logger.start_session(
        room_id=room_name,
        job_id=ctx.job.id,
        participant_id=getattr(ctx.job, 'participant_identity', None) or "unknown"
    )
    
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
    
    # Track collected user data and context
    user_data = {}
    last_agent_message = ""
    
    # Log conversation events
    @session.on("agent_speech_committed")
    def on_agent_speech(text: str):
        """Log agent speech to console and Supabase."""
        nonlocal last_agent_message
        last_agent_message = text
        print(f"Agent: {text}")
        import logging
        logging.info(f"Agent speech: {text}")
        asyncio.create_task(supabase_logger.log_message(
            room_id=room_name,
            participant_id="agent",
            role="agent",
            message=text
        ))
    
    @session.on("user_speech_committed")
    def on_user_speech(text: str):
        """Log user speech to console and Supabase."""
        print(f"User: {text}")
        import logging
        logging.info(f"User speech: {text}")
        asyncio.create_task(supabase_logger.log_message(
            room_id=room_name,
            participant_id=getattr(ctx.job, 'participant_identity', None) or "user",
            role="user",
            message=text
        ))
        
        # Extract and store user data from conversation
        text_lower = text.lower()
        
        # Extract name if in name collection state (basic heuristic)
        if len(user_data.get('user_name', '')) == 0:
            # Look for common name patterns after agent asks for name
            if any(phrase in last_agent_message.lower() for phrase in ['your first name', 'may i have your', 'what should i call']):
                # Simple name extraction - first word that's likely a name
                words = text.strip().split()
                if words and len(words[0]) > 1 and words[0].replace("'", "").replace("-", "").isalpha():
                    potential_name = words[0].capitalize()
                    user_data['user_name'] = potential_name
                    asyncio.create_task(supabase_logger.update_session_data(
                        room_name, 
                        {'user_name': potential_name}
                    ))
        
        # Check for email
        if '@' in text and '.' in text:
            import re
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            if email_match:
                email = email_match.group()
                user_data['user_email'] = email
                logging.info(f"Extracted email: {email}")
                asyncio.create_task(supabase_logger.update_session_data(
                    room_name, 
                    {'user_email': email}
                ))
        
        # Check for phone number (basic pattern)
        if any(char.isdigit() for char in text):
            import re
            # Match various phone formats
            phone_match = re.search(r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}', text)
            if phone_match and len(phone_match.group().replace(' ', '').replace('-', '').replace('.', '').replace('(', '').replace(')', '').replace('+', '')) >= 10:
                user_data['user_phone'] = phone_match.group()
                asyncio.create_task(supabase_logger.update_session_data(
                    room_name, 
                    {'user_phone': phone_match.group()}
                ))
    
    @session.on("function_calls_finished")
    def on_function_calls_finished(function_calls):
        """Log tool calls to Supabase."""
        for call in function_calls:
            asyncio.create_task(supabase_logger.log_tool_call(
                room_id=room_name,
                tool_name=call.function_info.name,
                parameters=call.arguments,
                result=str(call.result) if hasattr(call, 'result') else None,
                success=True
            ))
    
    # Add cleanup on disconnect
    @ctx.room.on("participant_disconnected")
    def on_participant_disconnected(participant: rtc.RemoteParticipant):
        """Handle participant disconnect."""
        job_participant = getattr(ctx.job, 'participant_identity', None)
        if job_participant and participant.identity == job_participant:
            asyncio.create_task(supabase_logger.end_session(room_name, 'completed'))
    
    # Also handle room disconnect
    @ctx.room.on("disconnected")
    def on_room_disconnected():
        """Handle room disconnect."""
        asyncio.create_task(supabase_logger.end_session(room_name, 'disconnected'))
    
    # Ensure cleanup on any exit
    try:
        await asyncio.Future()  # Keep running until cancelled
    except asyncio.CancelledError:
        await supabase_logger.end_session(room_name, 'cancelled')
        raise

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