import os
import asyncio
from datetime import datetime
from typing import AsyncIterable, Any, Coroutine
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice import Agent, AgentSession, ModelSettings
from livekit.plugins import openai, deepgram, cartesia, silero
from supabase import create_client, Client

# Import Google Calendar tools
from google_calendar_tools import (
    google_calendar_check_real_availability,
    google_calendar_create_meeting
)

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = None
if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class CustomAssistant(Agent):
    def __init__(self) -> None:
        # Initialize with the calendar tools
        super().__init__(
            tools=[
                google_calendar_check_real_availability,
                google_calendar_create_meeting
            ],
            instructions="""You are Elliot from Botel AI, an AI voice assistant.

CRITICAL: When handling calendar operations:
1. For availability checks: Respond ONLY with the tool call, no text
2. For meeting creation: Respond ONLY with the tool call, no text
3. After getting tool results, then speak naturally

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

## 4. Scheduling Process

Step 1 – Confirm Email:
Perfect. Before we pick a time, can you confirm the best email for the invite? I have it as [contact email]—is that still correct?

Step 2 – When they confirm email:
[Use google_calendar_check_real_availability tool ONLY - no text]

Step 3 – When they pick a time:
[Use google_calendar_create_meeting tool ONLY - no text]

## 5. FAQs on Pricing & Integrations

- Pricing: from 10 dollars per property per month
- Integrations: Guesty, Hostaway, Lodgify

[Rest of the script continues as before...]"""
        )
    
    def llm_node(
        self,
        chat_ctx: llm.ChatContext,
        tools: list[llm.FunctionTool | llm.RawFunctionTool],
        model_settings: ModelSettings,
    ) -> AsyncIterable[llm.ChatChunk | str] | Coroutine[Any, Any, AsyncIterable[llm.ChatChunk | str]]:
        """
        Override the LLM node to handle tool-only responses better.
        
        This custom implementation ensures that when the LLM wants to call a tool,
        it doesn't generate any preceding text that would cause a pause.
        """
        # Check if this is a calendar-related query that should trigger immediate tool use
        if chat_ctx.items:
            last_message = chat_ctx.items[-1]
            if hasattr(last_message, 'content') and isinstance(last_message.content, list):
                user_text = ' '.join([str(c) for c in last_message.content]).lower()
                
                # If user just confirmed email, we need to check availability
                if any(keyword in user_text for keyword in ['yes', 'correct', 'that\'s right', '@']) and \
                   any(keyword in user_text for keyword in ['email', 'correct']):
                    # Force tool-only response
                    model_settings = ModelSettings(tool_choice="required")
                
                # If user picked a time, we need to create meeting
                elif any(day in user_text for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']) or \
                     any(time_indicator in user_text for time_indicator in ['pm', 'am', 'o\'clock', ':00']):
                    # Force tool-only response
                    model_settings = ModelSettings(tool_choice="required")
        
        # Use the default implementation with potentially modified settings
        return Agent.default.llm_node(self, chat_ctx, tools, model_settings)

async def entrypoint(ctx: JobContext):
    """Main entry point for the voice agent."""
    # Configure the voice session with all components
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-2",
            language="en",
        ),
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7,
            parallel_tool_calls=False,  # Execute tools sequentially
            tool_choice="auto",  # Let the model decide when to use tools
        ),
        tts=cartesia.TTS(
            voice="f786b574-daa5-4673-aa0c-cbe3e8534c02",
        ),
        vad=silero.VAD.load(),
    )
    
    # Connect to the room
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # Create the assistant
    assistant = CustomAssistant()
    
    # Start the agent session
    await session.start(
        room=ctx.room,
        agent=assistant,
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