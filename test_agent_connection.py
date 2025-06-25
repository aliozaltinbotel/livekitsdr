#!/usr/bin/env python3
"""Test script to verify LiveKit agent connection."""

import os
import asyncio
import logging
from dotenv import load_dotenv
from livekit.api import LiveKitAPI, CreateRoomRequest, DeleteRoomRequest, ListRoomsRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv("agent/.env")

async def test_connection():
    """Test LiveKit connection and room creation."""
    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not all([url, api_key, api_secret]):
        logger.error("Missing required environment variables")
        return
    
    logger.info(f"Testing connection to: {url}")
    
    try:
        # Create a LiveKit API client
        livekit_api = LiveKitAPI(
            url.replace("wss://", "https://").replace("ws://", "http://"),
            api_key,
            api_secret
        )
        
        # List existing rooms
        logger.info("Listing existing rooms...")
        response = await livekit_api.room.list_rooms(ListRoomsRequest())
        logger.info(f"Found {len(response.rooms)} rooms")
        for room in response.rooms:
            logger.info(f"  - Room: {room.name} (participants: {room.num_participants})")
        
        # Create a test room
        test_room_name = "test_agent_room"
        logger.info(f"Creating test room: {test_room_name}")
        
        try:
            room = await livekit_api.room.create_room(
                CreateRoomRequest(
                    name=test_room_name,
                    metadata="{\"agent_required\": true}"
                )
            )
            logger.info(f"Room created successfully: {room.name}")
            
            # Wait a bit to see if agent joins
            logger.info("Waiting 5 seconds for agent to join...")
            await asyncio.sleep(5)
            
            # Check room again
            response = await livekit_api.room.list_rooms(ListRoomsRequest())
            for room in response.rooms:
                if room.name == test_room_name:
                    logger.info(f"Test room participants: {room.num_participants}")
                    if room.num_participants > 0:
                        logger.info("✅ Agent successfully joined the room!")
                    else:
                        logger.warning("⚠️  Agent did not join the room")
            
            # Clean up
            logger.info("Deleting test room...")
            await livekit_api.room.delete_room(DeleteRoomRequest(room=test_room_name))
            
        except Exception as e:
            logger.error(f"Error creating/managing room: {e}")
            
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'livekit_api' in locals():
            await livekit_api.aclose()

if __name__ == "__main__":
    asyncio.run(test_connection())