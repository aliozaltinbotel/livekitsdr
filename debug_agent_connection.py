#!/usr/bin/env python3
"""
Debug script to test agent connection to LiveKit rooms
"""
import os
import asyncio
import logging
from dotenv import load_dotenv
from livekit import api

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_agent_dispatch():
    """Check agent dispatch configuration"""
    
    # Create API client
    livekit_api = api.LiveKitAPI(
        os.getenv("LIVEKIT_URL"),
        os.getenv("LIVEKIT_API_KEY"),
        os.getenv("LIVEKIT_API_SECRET")
    )
    
    logger.info("LiveKit API Configuration:")
    logger.info(f"URL: {os.getenv('LIVEKIT_URL')}")
    logger.info(f"API Key: {os.getenv('LIVEKIT_API_KEY')[:10]}...")
    
    # List active rooms
    try:
        rooms = await livekit_api.room.list_rooms()
        logger.info(f"\nActive rooms: {len(rooms)}")
        for room in rooms:
            logger.info(f"  - Room: {room.name}, Participants: {room.num_participants}")
    except Exception as e:
        logger.error(f"Failed to list rooms: {e}")
    
    # Check agent info
    logger.info("\nAgent Configuration:")
    logger.info("Agent Name: voice-assistant")
    logger.info("Room Pattern: Not configured (accepts all rooms)")
    logger.info("\nPotential Issues:")
    logger.info("1. Agent dispatch rules not configured in LiveKit Cloud")
    logger.info("2. Agent not registered with correct namespace")
    logger.info("3. Room metadata not matching agent requirements")
    
    logger.info("\nSolution:")
    logger.info("Configure agent dispatch in LiveKit Cloud dashboard:")
    logger.info("1. Go to https://cloud.livekit.io")
    logger.info("2. Navigate to your project -> Agents")
    logger.info("3. Configure dispatch rules for 'voice-assistant' agent")
    logger.info("4. Set room name pattern: 'voice_assistant_room_*' or dispatch to all rooms")

if __name__ == "__main__":
    asyncio.run(check_agent_dispatch())