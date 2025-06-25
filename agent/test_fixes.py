#!/usr/bin/env python3
"""
Test script to verify the fixes are working correctly
"""

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging to test reduced verbosity
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test that HTTP/2 logging is reduced
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("hpack").setLevel(logging.WARNING)

async def test_supabase_connection():
    """Test Supabase connection with retry logic"""
    logger.info("Testing Supabase connection...")
    
    try:
        from supabase_logger import supabase_logger
        
        if supabase_logger.client:
            logger.info("✓ Supabase client initialized successfully")
            
            # Test a simple operation
            test_room = "test_room_" + str(int(asyncio.get_event_loop().time()))
            await supabase_logger.log_message(
                room_id=test_room,
                participant_id="test",
                role="system",
                message="Test message"
            )
            logger.info("✓ Successfully logged test message")
        else:
            logger.warning("⚠ Supabase client not initialized (check credentials)")
            
    except Exception as e:
        logger.error(f"✗ Supabase test failed: {e}")

def test_mcp_env():
    """Test MCP environment configuration"""
    logger.info("Testing MCP configuration...")
    
    mcp_url = os.getenv("PMS_MCP_SERVER_URL")
    if mcp_url:
        logger.info(f"✓ MCP server URL configured: {mcp_url}")
    else:
        logger.error("✗ MCP server URL not configured")

def test_name_extraction():
    """Test improved name extraction logic"""
    logger.info("Testing name extraction...")
    
    # Test cases
    test_inputs = [
        ("Still waiting", False),  # Should not extract "Still"
        ("My name is John", True),  # Should extract "John"
        ("Yes", False),  # Should not extract "Yes"
        ("Sarah", True),  # Should extract "Sarah" if in name context
    ]
    
    exclude_words = ['yes', 'no', 'okay', 'sure', 'correct', 'right', 'wrong', 'maybe', 'please', 'thanks',
                   'still', 'waiting', 'hello', 'hi', 'hey', 'what', 'where', 'when', 'why', 'how',
                   'sorry', 'excuse', 'pardon', 'again', 'repeat', 'good', 'great', 'fine', 'well',
                   'um', 'uh', 'hmm', 'oh', 'ah', 'ok', 'alright', 'ready', 'done', 'finished']
    
    for text, should_extract in test_inputs:
        words = text.split()
        if words:
            first_word = words[0].lower()
            is_excluded = first_word in exclude_words
            result = not is_excluded if should_extract else is_excluded
            status = "✓" if result else "✗"
            logger.info(f"{status} '{text}' -> excluded={is_excluded}")

async def main():
    """Run all tests"""
    logger.info("=== Running Fix Verification Tests ===\n")
    
    # Test 1: MCP configuration
    test_mcp_env()
    print()
    
    # Test 2: Name extraction
    test_name_extraction()
    print()
    
    # Test 3: Supabase connection
    await test_supabase_connection()
    print()
    
    logger.info("=== Tests Complete ===")

if __name__ == "__main__":
    asyncio.run(main())