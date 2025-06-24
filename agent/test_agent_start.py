#!/usr/bin/env python3
"""
Simple test script to start the LiveKit agent
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Print environment variables to debug
print("Environment Variables:")
print(f"LIVEKIT_URL: {os.getenv('LIVEKIT_URL')}")
print(f"LIVEKIT_API_KEY: {os.getenv('LIVEKIT_API_KEY')}")
print(f"LIVEKIT_API_SECRET: {'Set' if os.getenv('LIVEKIT_API_SECRET') else 'Not set'}")
print(f"PMS_MCP_SERVER_URL: {os.getenv('PMS_MCP_SERVER_URL')}")
print()

# Now try to start the agent
try:
    # Import after loading env vars
    from livekit.agents import cli
    
    # Use the azure_working agent which doesn't have MCP imports
    from agent_azure_working import Assistant, entrypoint, WorkerOptions
    
    print("Starting LiveKit agent in development mode...")
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
    
except Exception as e:
    print(f"Error starting agent: {e}")
    import traceback
    traceback.print_exc()