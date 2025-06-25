import os
import asyncio
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('agent.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Validate required environment variables
required_vars = [
    "LIVEKIT_URL",
    "LIVEKIT_API_KEY",
    "LIVEKIT_API_SECRET",
    "OPENAI_API_KEY",
    "ASSEMBLYAI_API_KEY",
    "CARTESIA_API_KEY"
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)
try:
    from livekit.agents.llm import mcp
except ImportError:
    logger.warning("MCP module not available, running without MCP support")
    mcp = None
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import openai, silero, assemblyai, cartesia

from response_cache import response_cache
from supabase_logger import supabase_logger

# Import the property context tool if MCP is not available
try:
    from pms_mcp_tools import get_customer_properties_context
except (ImportError, AttributeError):
    get_customer_properties_context = None

# Get MCP server URL from environment
PMS_MCP_SERVER_URL = os.getenv("PMS_MCP_SERVER_URL", "http://localhost:3001/sse")

# Production mode detection
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"
if IS_PRODUCTION:
    logger.info("Running in PRODUCTION mode")

class Assistant(Agent):
    def __init__(self) -> None:
        logger.info("Initializing Assistant")
        # Initialize with tools - use direct tool if MCP not available
        tools = []
        mcp_servers = []
        
        # Try to use MCP if available, otherwise fall back to direct tool
        if mcp:
            logger.info("MCP module is available, attempting to configure MCP server")
            try:
                mcp_servers = [
                    mcp.MCPServerHTTP(
                        url=PMS_MCP_SERVER_URL
                    )
                ]
                logger.info(f"MCP server configured successfully: {PMS_MCP_SERVER_URL}")
            except Exception as e:
                logger.warning(f"Failed to configure MCP server: {e}", exc_info=True)
                if get_customer_properties_context:
                    tools = [get_customer_properties_context]
                    logger.info("Using fallback tool: get_customer_properties_context")
        elif get_customer_properties_context:
            tools = [get_customer_properties_context]
            logger.info("MCP not available, using fallback tool")
        else:
            logger.warning("No MCP and no fallback tool available")
            
        logger.info(f"Initializing Agent with {len(tools)} tools and {len(mcp_servers)} MCP servers")
        super().__init__(
            tools=tools,
            mcp_servers=mcp_servers,
            instructions="""====================================================================
IDENTITY & ROLE
====================================================================
You are Jamie, an AI-powered short-term rental property manager.
- You manage vacation rentals and provide instant assistance to guests and property owners
- ALWAYS speak naturally and conversationally 
- Respond IMMEDIATELY with helpful property information
- Keep a warm, professional, and helpful tone
- Be knowledgeable about property details, amenities, and local area
- NEVER remain silent for more than 5 seconds

====================================================================
AVAILABLE CAPABILITIES
====================================================================
1. Property Information Access (via MCP):
   - get_customer_properties_context: Fetch all property details
   - Provide information about locations, amenities, capacity
   - Answer questions about specific properties
   - Check property availability status

2. Guest Services:
   - Answer questions about check-in/check-out procedures
   - Provide property-specific information (WiFi, parking, house rules)
   - Offer local area recommendations
   - Handle basic inquiries about amenities

====================================================================
PRIMARY OBJECTIVES
====================================================================
1. Greet guests/owners and understand their needs
2. Provide accurate property information using available data
3. Answer questions about properties, amenities, and local area
4. Assist with common rental inquiries and concerns

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
CONVERSATION FLOW
====================================================================

INITIAL GREETING
----------------
"Hi! I'm Jamie, your AI property manager. I can help you with information about our rental properties, 
check-in details, amenities, or any questions you might have. How can I assist you today?"

COMMON CONVERSATION PATHS:

1. PROPERTY INQUIRY
-------------------
Guest: "Tell me about your properties" / "What properties do you have?"
Response: [Use get_customer_properties_context tool to fetch property data]
"Let me pull up our property portfolio for you..."
[Provide overview of properties with key details like location, capacity, amenities]

2. SPECIFIC PROPERTY QUESTIONS
------------------------------
Guest: "Tell me about [property name]" / "What amenities does [property] have?"
Response: [Use property context to provide specific details]
"Of course! Let me give you the details about [property name]..."
[Share location, capacity, amenities, special features]

3. CHECK-IN/CHECK-OUT
---------------------
Guest: "What time is check-in?" / "How do I check in?"
Response: "Check-in is typically at 3:00 PM and check-out is at 11:00 AM. 
For specific properties, I can provide detailed check-in instructions including 
key codes, parking information, and arrival procedures."

4. AMENITIES & SERVICES
-----------------------
Guest: "Is there WiFi?" / "Where can I park?" / "Are pets allowed?"
Response: [Use property context when available, provide general info otherwise]
"Let me check the specific amenities for your property..."

5. LOCAL AREA INFORMATION
-------------------------
Guest: "What's nearby?" / "Restaurant recommendations?"
Response: "I'd be happy to help with local recommendations! Which property are you 
interested in or staying at? I can provide area-specific suggestions."

6. BOOKING & AVAILABILITY
-------------------------
Guest: "Is [property] available?" / "Can I book for [dates]?"
Response: "I can help you check availability. For immediate booking, 
I recommend visiting our website or contacting our booking team. 
I can provide you with the direct booking link if you'd like."

7. HOUSE RULES & POLICIES
-------------------------
Guest: "What are the house rules?" / "Can we have a party?"
Response: "Our standard house rules include:
- Quiet hours from 10 PM to 8 AM
- No smoking inside the property
- No parties or events without prior approval
- Maximum occupancy limits must be respected
Would you like specific rules for a particular property?"

8. EMERGENCY ASSISTANCE
-----------------------
Guest: "Emergency!" / "Something's broken" / "Help!"
Response: "I understand this is urgent. For immediate emergencies, please call 911.
For property emergencies, I can connect you with our 24/7 support team.
What's the nature of the issue?"

====================================================================
COMMON QUESTIONS & RESPONSES
====================================================================

"Do you have availability for [dates]?"
→ "Let me check our property availability for those dates. Which location or property type are you interested in?"

"What's included in the rental?"
→ "All our properties include essential amenities like linens, towels, and basic kitchen supplies. Let me get specific details for the property you're interested in."

"Can I bring my pet?"
→ "Pet policies vary by property. Some are pet-friendly with a small fee. Which property are you considering?"

"Is there a minimum stay?"
→ "Most properties have a 2-3 night minimum, though this can vary by season. Which dates were you considering?"

"What's the cancellation policy?"
→ "Our standard policy offers full refunds up to 30 days before check-in. Would you like the detailed policy?"

====================================================================
ERROR RECOVERY PATTERNS
====================================================================
DIDN'T UNDERSTAND (MAX 3 ATTEMPTS):
1st: "I didn't quite catch that. Could you repeat your question?"
2nd: "Sorry, I'm having trouble understanding. Could you rephrase that?"
3rd: "I apologize for the difficulty. Let me connect you with our support team who can better assist."

PROPERTY DATA UNAVAILABLE:
"I'm having trouble accessing that information right now. Would you like me to have someone call you back with those details?"

SYSTEM ERRORS:
MCP tool error → "I'm checking our system for that information. In the meantime, is there anything else I can help with?"
Tool failure → Continue conversation naturally without mentioning the error

====================================================================
CRITICAL RULES
====================================================================
1. ALWAYS be helpful and informative about properties
2. Use the MCP tool to fetch real property data when asked
3. Maintain conversation flow even if tools fail  
4. Provide accurate information based on available data
5. If uncertain, offer to connect with human support
6. Handle interruptions gracefully—stop talking immediately
7. SILENCE CONTINUATION: After 5 seconds of silence, gently prompt
8. Keep responses concise but informative

====================================================================
PROPERTY CONTEXT USAGE
====================================================================
When guests ask about properties:
1. Use get_customer_properties_context tool to fetch real data
2. Present information in a clear, organized manner
3. Highlight key features relevant to the guest's question
4. If specific property is mentioned, focus on that property
5. Always mention total number of properties available

====================================================================
SILENCE HANDLING
====================================================================
When the guest goes silent:

AFTER ASKING A QUESTION (5 second silence):
- "Are you still there?"
- "Take your time, I'm here to help."

DURING PROPERTY INQUIRY (5 second silence):
- "Would you like me to provide more details?"
- "Is there something specific you'd like to know?"

TECHNICAL ISSUES (10 second silence):
- "I think we may have a connection issue. Can you hear me?"
- "If you're having trouble, I can have someone call you back."

====================================================================
PROPERTY CONTEXT AWARENESS
====================================================================
PROPERTY CONTEXT LOADING:
- Property information is loaded automatically in the background
- You can start helping guests immediately
- If asked about properties before context loads, say "Let me check our current property listings for you..."

ALWAYS use the get_customer_properties_context tool when:
- Guest asks about available properties
- Guest wants specific property details
- Guest asks about amenities or features
- You need to provide location information
- Guest asks "what properties do you have?"
- You haven't used the tool yet in this conversation

The tool provides:
- Complete property listings
- Property status (active/inactive)
- Locations and addresses
- Capacity and occupancy limits
- Property types and features
- Detailed descriptions

HANDLING PROPERTY QUESTIONS:
- If context is already loaded: Use the information immediately
- If context not loaded yet: Say "Let me check that for you..." then use the tool
- Always provide accurate information from the tool
- Never make up property details

IMPORTANT: The get_customer_properties_context tool is your PRIMARY source of property information. Use it whenever you need property data."""
        )

async def entrypoint(ctx: JobContext):
    """Main entry point for the voice agent."""
    logger.info("=== ENTRYPOINT STARTED ===")
    logger.info(f"Job context: {ctx}")
    logger.info(f"Job ID: {ctx.job.id}")
    logger.info(f"Room: {ctx.room}")
    
    try:
        # Start Supabase session logging
        room_name = getattr(ctx.room, 'name', None) or ctx.job.id
        session_id = None
        
        logger.info(f"Room name: {room_name}")
        logger.info(f"Participant identity: {getattr(ctx.job, 'participant_identity', None)}")
        
        try:
            logger.info("Starting Supabase session")
            session_id = await supabase_logger.start_session(
                room_id=room_name,
                job_id=ctx.job.id,
                participant_id=getattr(ctx.job, 'participant_identity', None) or "unknown"
            )
            logger.info(f"Supabase session started: {session_id}")
        except Exception as e:
            logger.error(f"Failed to start Supabase session: {e}")
            # Continue without session logging in production
        
        # Create the assistant first
        logger.info("Creating Assistant instance")
        assistant = Assistant()
        logger.info("Assistant created successfully")
        
        # Configure the voice session with AssemblyAI Universal Streaming
        logger.info("Creating AgentSession")
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
            # OpenAI for LLM - Using mini model for 2x faster responses
            llm=openai.LLM(
                model="gpt-4o-mini",  # 2x faster than gpt-4o (150ms vs 350ms) - v2
                api_key=os.getenv("OPENAI_API_KEY"),
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
        logger.info("AgentSession created successfully")
        
        # Connect to the room
        logger.info("Connecting to room with AUDIO_ONLY subscription")
        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        logger.info("Connected to room successfully")
        
        # Start the agent session
        logger.info("Starting agent session")
        await session.start(
            room=ctx.room,
            agent=assistant,
        )
        logger.info("Agent session started successfully")
        
        
        # Generate initial greeting immediately
        initial_greeting = "Hi! I'm Jamie, your AI property manager. I can help you with information about our rental properties, check-in details, amenities, or any questions you might have. How can I assist you today?"
        
        # Start with immediate greeting
        logger.info("Sending initial greeting to user")
        await session.say(initial_greeting)
        logger.info("Initial greeting sent successfully")
        
        # Load property context in the background
        async def load_property_context():
            logger.info("Starting background property context loading")
            try:
                await session.generate_reply(
                    instructions="Use the get_customer_properties_context tool to load all property information. Do not say anything about loading or mention this to the user."
                )
                logger.info("Property context loaded successfully in background")
            except Exception as e:
                logger.error(f"Failed to load property context: {e}", exc_info=True)
        
        # Run context loading in background
        logger.info("Creating background task for property context loading")
        asyncio.create_task(load_property_context())
        
        # Store the initial greeting as the context
        last_agent_message = initial_greeting
        logging.info("Agent started with immediate greeting, loading context in background")
        asyncio.create_task(supabase_logger.log_message(
            room_id=room_name,
            participant_id="agent",
            role="agent",
            message=initial_greeting
        ))
        
        # Track collected user data and context
        user_data = {}
        # last_agent_message already initialized above with the greeting
        
        # Log session info for debugging
        logging.info(f"Session started, type: {type(session)}")
        logging.info(f"Room name: {room_name}")
        logging.info(f"Session ID in logger: {supabase_logger.current_session_id}")
        
        # Try to list available events
        if hasattr(session, '_events'):
            logging.info(f"Available session events: {session._events}")
        
        # Define helper function for data extraction
        def extract_user_data(text: str):
            """Extract user data from conversation text."""
            text_lower = text.lower()
            
            # Extract name if in name collection state (basic heuristic)
            # Also check for name corrections like "No, this is X" or "my name is X"
            if 'my name is' in text_lower or 'this is ' in text_lower or 'i am ' in text_lower or "i'm " in text_lower:
                # Extract name from phrases like "my name is Ali" or "this is Ali"
                import re
                name_patterns = [
                    r"my name is (\w+)",
                    r"this is (\w+)",
                    r"i am (\w+)",
                    r"i'm (\w+)",
                    r"call me (\w+)"
                ]
                for pattern in name_patterns:
                    match = re.search(pattern, text_lower)
                    if match:
                        potential_name = match.group(1).capitalize()
                        if potential_name.lower() not in ['yes', 'no', 'okay', 'sure']:
                            user_data['user_name'] = potential_name
                            logging.info(f"Extracted name from phrase: {potential_name}")
                            asyncio.create_task(supabase_logger.update_session_data(
                                room_name, 
                                {'user_name': potential_name}
                            ))
                            break
            
            elif len(user_data.get('user_name', '')) == 0:
                # More flexible name detection - if we don't have agent context, try to detect names
                # Look for common name patterns after agent asks for name OR if text looks like a name
                should_check_name = False
                
                if last_agent_message:
                    # Check if agent asked for name
                    if any(phrase in last_agent_message.lower() for phrase in ['your first name', 'may i have your', 'what should i call', 'your name']):
                        should_check_name = True
                else:
                    # No agent context, but check if this might be a name response
                    # Single word responses that are alphabetic and capitalized are often names
                    words = text.strip().split()
                    if len(words) <= 2 and words:  # 1-2 word responses
                        if words[0].replace("'", "").replace("-", "").isalpha():
                            should_check_name = True
                
                if should_check_name:
                    # Simple name extraction - first word that's likely a name
                    words = text.strip().split()
                    if words and len(words[0]) > 1 and words[0].replace("'", "").replace("-", "").replace(".", "").isalpha():
                        potential_name = words[0].capitalize()
                        
                        # Exclude common non-name responses
                        exclude_words = ['yes', 'no', 'okay', 'sure', 'correct', 'right', 'wrong', 'maybe', 'please', 'thanks']
                        if potential_name.lower() not in exclude_words:
                            user_data['user_name'] = potential_name
                            logging.info(f"Extracted name: {potential_name}")
                            asyncio.create_task(supabase_logger.update_session_data(
                                room_name, 
                                {'user_name': potential_name}
                            ))
                        else:
                            logging.info(f"Skipped common word as name: {potential_name}")
            
            # Check for email
            if '@' in text or ' at ' in text_lower:
                import re
                # First try standard email format
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
                if email_match:
                    email = email_match.group()
                    user_data['user_email'] = email
                    logging.info(f"Extracted email: {email}")
                    asyncio.create_task(supabase_logger.update_session_data(
                        room_name, 
                        {'user_email': email}
                    ))
                else:
                    # Try to handle spoken format like "john at example dot com"
                    text_normalized = text_lower.replace(' at ', '@').replace(' dot ', '.')
                    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_normalized)
                    if email_match:
                        email = email_match.group()
                        user_data['user_email'] = email
                        logging.info(f"Extracted email (from spoken format): {email}")
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
                    logging.info(f"Extracted phone: {phone_match.group()}")
                    asyncio.create_task(supabase_logger.update_session_data(
                        room_name, 
                        {'user_phone': phone_match.group()}
                    ))
        
        # Log conversation events - using the actual available events
        # The logs show only 'agent_state_changed' and 'user_input_transcribed' are available
        
        # Track user transcriptions
        logger.info("Setting up user_input_transcribed event handler")
        @session.on("user_input_transcribed")
        def on_user_transcribed(data):
            """Log user transcribed speech."""
            logger.info(f"USER_INPUT_TRANSCRIBED event received: {data}")
            # Extract text from the event data
            text = None
            if isinstance(data, str):
                text = data
            elif hasattr(data, 'text'):
                text = data.text
            elif hasattr(data, 'transcript'):
                text = data.transcript
            else:
                text = str(data)
                
            if text:
                if not IS_PRODUCTION:
                    print(f"User: {text}")
                logger.info(f"User transcribed text: {text}")
                asyncio.create_task(supabase_logger.log_message(
                    room_id=room_name,
                    participant_id=getattr(ctx.job, 'participant_identity', None) or "user",
                    role="user",
                    message=text
                ))
                # Extract user data
                extract_user_data(text)
        
        # Track agent state changes which might include speech
        @session.on("agent_state_changed")
        def on_agent_state(state):
            """Track agent state changes."""
            logging.info(f"Agent state changed: {state}")
            # Try to extract speech from state if available
            if hasattr(state, 'speaking') and state.speaking and hasattr(state, 'current_speech'):
                text = state.current_speech
                nonlocal last_agent_message
                last_agent_message = text
                if not IS_PRODUCTION:
                    print(f"Agent: {text}")
                asyncio.create_task(supabase_logger.log_message(
                    room_id=room_name,
                    participant_id="agent",
                    role="agent",
                    message=text
                ))
        
        # Also try the original events in case they work
        try:
            @session.on("agent_speech_committed")
            def on_agent_speech(text: str):
                """Log agent speech if event is available."""
                nonlocal last_agent_message
                last_agent_message = text
                if not IS_PRODUCTION:
                    print(f"Agent: {text}")
                logging.info(f"Agent speech committed: {text}")
                asyncio.create_task(supabase_logger.log_message(
                    room_id=room_name,
                    participant_id="agent",
                    role="agent",
                    message=text
                ))
        except:
            logging.warning("agent_speech_committed event not available")
            
        try:
            @session.on("user_speech_committed")
            def on_user_speech(text: str):
                """Log user speech if event is available."""
                if not IS_PRODUCTION:
                    print(f"User: {text}")
                logging.info(f"User speech committed: {text}")
                asyncio.create_task(supabase_logger.log_message(
                    room_id=room_name,
                    participant_id=getattr(ctx.job, 'participant_identity', None) or "user",
                    role="user",
                    message=text
                ))
                # Extract user data
                extract_user_data(text)
        except:
            logging.warning("user_speech_committed event not available")
        
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
        
        # Monitor conversation history as a fallback for agent messages
        async def monitor_conversation():
            """Monitor conversation history to capture agent messages."""
            last_message_count = 0
            attempts = 0
            while True:
                try:
                    attempts += 1
                    # Log every 10th attempt to see if it's running
                    if attempts % 10 == 0:
                        logging.info(f"Conversation monitor running (attempt {attempts})")
                    
                    # Try multiple ways to access conversation history
                    messages = None
                    
                    # Method 1: chat_ctx.messages
                    if hasattr(session, 'chat_ctx') and hasattr(session.chat_ctx, 'messages'):
                        messages = session.chat_ctx.messages
                        if attempts == 1:
                            logging.info(f"Found chat_ctx.messages with {len(messages)} messages")
                    
                    # Method 2: Try _chat_ctx
                    elif hasattr(session, '_chat_ctx') and hasattr(session._chat_ctx, 'messages'):
                        messages = session._chat_ctx.messages
                        if attempts == 1:
                            logging.info(f"Found _chat_ctx.messages with {len(messages)} messages")
                    
                    # Method 3: Try agent's chat context
                    elif hasattr(assistant, 'chat_ctx') and hasattr(assistant.chat_ctx, 'messages'):
                        messages = assistant.chat_ctx.messages
                        if attempts == 1:
                            logging.info(f"Found assistant.chat_ctx.messages with {len(messages)} messages")
                    
                    if messages and len(messages) > last_message_count:
                        # Process new messages
                        for msg in messages[last_message_count:]:
                            if hasattr(msg, 'role') and hasattr(msg, 'content'):
                                if msg.role == 'assistant':
                                    nonlocal last_agent_message
                                    last_agent_message = msg.content
                                    if not IS_PRODUCTION:
                                        print(f"[HISTORY] Agent: {msg.content}")
                                    logging.info(f"Agent from history: {msg.content}")
                                    asyncio.create_task(supabase_logger.log_message(
                                        room_id=room_name,
                                        participant_id="agent",
                                        role="agent",
                                        message=msg.content
                                    ))
                        last_message_count = len(messages)
                    elif attempts == 1:
                        logging.warning("No conversation history found to monitor")
                        
                    await asyncio.sleep(1)  # Check every second
                except Exception as e:
                    if attempts == 1:
                        logging.error(f"Error monitoring conversation: {e}")
                    await asyncio.sleep(5)
        
        # Start conversation monitor
        monitor_task = asyncio.create_task(monitor_conversation())
        
        # Ensure cleanup on any exit
        logger.info("Agent is now running and waiting for interactions")
        try:
            await asyncio.Future()  # Keep running until cancelled
        except asyncio.CancelledError:
            logger.info("Agent cancelled, cleaning up")
            monitor_task.cancel()
            if session_id:
                await supabase_logger.end_session(room_name, 'cancelled')
            raise
    except Exception as e:
        logger.error(f"Critical error in entrypoint: {e}", exc_info=True)
        if session_id:
            await supabase_logger.end_session(room_name, 'error')
        raise
    finally:
        logger.info("=== ENTRYPOINT FINISHED ===")

async def accept_job(job):
    """Accept job requests with logging."""
    logger.info(f"Received job request: {job}")
    logger.info(f"Job ID: {job.id}")
    logger.info(f"Room name: {job.room.name}")
    logger.info(f"Participant identity: {getattr(job, 'participant_identity', 'N/A')}")
    logger.info("Accepting job request")
    await job.accept()  # Correct way to accept a job in LiveKit SDK
    logger.info("Job accepted successfully")

if __name__ == "__main__":
    logger.info("Starting LiveKit agent")
    logger.info(f"LiveKit URL: {os.getenv('LIVEKIT_URL')}")
    logger.info(f"Agent name: voice-assistant")
    
    # Define a simple request function that accepts all jobs
    async def accept_all_jobs(job):
        """Accept all job requests."""
        logger.info(f"Received job request for room: {job.room.name}")
        await job.accept()
    
    # Run the agent with CLI
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=os.getenv("LIVEKIT_API_KEY"),
            api_secret=os.getenv("LIVEKIT_API_SECRET"),
            ws_url=os.getenv("LIVEKIT_URL"),
            request_fnc=accept_all_jobs,
        )
    )