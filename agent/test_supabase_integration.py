#!/usr/bin/env python3
"""
Test script to verify Supabase integration is working correctly
"""

import asyncio
import os
from datetime import datetime
from supabase_logger import supabase_logger

async def test_supabase_operations():
    """Test all Supabase operations"""
    
    print("Testing Supabase Integration...")
    print("=" * 50)
    
    # Test 1: Start a session
    test_room_id = f"test_room_{datetime.now().timestamp()}"
    test_job_id = "test_job_123"
    test_participant_id = "test_participant"
    
    print(f"\n1. Starting session: {test_room_id}")
    session_id = await supabase_logger.start_session(
        room_id=test_room_id,
        job_id=test_job_id,
        participant_id=test_participant_id
    )
    
    if session_id:
        print(f"   ✓ Session started successfully: {session_id}")
    else:
        print("   ✗ Failed to start session")
        return
    
    # Test 2: Log messages
    print("\n2. Logging messages...")
    
    # Log agent message
    await supabase_logger.log_message(
        room_id=test_room_id,
        participant_id="agent",
        role="agent",
        message="Hello! This is a test agent message."
    )
    print("   ✓ Agent message logged")
    
    # Log user message
    await supabase_logger.log_message(
        room_id=test_room_id,
        participant_id="user",
        role="user",
        message="This is a test user response."
    )
    print("   ✓ User message logged")
    
    # Test 3: Update session data
    print("\n3. Updating session data...")
    
    # Update with user name
    await supabase_logger.update_session_data(
        test_room_id,
        {'user_name': 'Test User'}
    )
    print("   ✓ Updated user name")
    
    # Update with email
    await supabase_logger.update_session_data(
        test_room_id,
        {'user_email': 'test@example.com'}
    )
    print("   ✓ Updated user email")
    
    # Update with phone
    await supabase_logger.update_session_data(
        test_room_id,
        {'user_phone': '+1234567890'}
    )
    print("   ✓ Updated user phone")
    
    # Test 4: Log tool call
    print("\n4. Logging tool call...")
    await supabase_logger.log_tool_call(
        room_id=test_room_id,
        tool_name="google_calendar_check_availability",
        parameters={"timezone": "America/New_York"},
        result="Available times: Monday 2pm, Tuesday 10am",
        success=True
    )
    print("   ✓ Tool call logged")
    
    # Test 5: Mark demo scheduled
    print("\n5. Marking demo as scheduled...")
    await supabase_logger.mark_demo_scheduled(
        room_id=test_room_id,
        demo_time="2025-06-25T14:00:00-04:00",
        timezone="America/New_York"
    )
    print("   ✓ Demo marked as scheduled")
    
    # Test 6: End session
    print("\n6. Ending session...")
    await supabase_logger.end_session(test_room_id, 'completed')
    print("   ✓ Session ended")
    
    print("\n" + "=" * 50)
    print("Test completed! Check your Supabase dashboard to verify the data.")
    print(f"\nLook for session ID: {test_room_id}")

if __name__ == "__main__":
    # Check if environment variables are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("ERROR: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        exit(1)
    
    # Run the test
    asyncio.run(test_supabase_operations())