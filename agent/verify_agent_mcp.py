#!/usr/bin/env python3
"""Verify agent MCP configuration"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Verifying Agent MCP Configuration")
print("="*60)

# Check imports
try:
    from livekit.agents.llm import mcp
    print("✅ MCP module imported successfully")
except ImportError as e:
    print(f"❌ MCP module import failed: {e}")
    print("   Make sure to install: pip install livekit-agents[mcp]>=1.1.4")

# Check MCP server URL
mcp_url = os.getenv("PMS_MCP_SERVER_URL", "http://localhost:3001/sse")
print(f"\n✅ MCP Server URL: {mcp_url}")

# Check if MCP server is accessible
import requests
try:
    # Try to connect to MCP server health endpoint
    health_url = mcp_url.replace("/sse", "").replace("http://", "http://").rstrip("/") + "/health"
    response = requests.get(health_url, timeout=5)
    if response.status_code == 200:
        print(f"✅ MCP Server is accessible at {health_url}")
        print(f"   Response: {response.json()}")
    else:
        print(f"⚠️  MCP Server returned status {response.status_code}")
except Exception as e:
    print(f"❌ Cannot reach MCP Server: {e}")
    print("   Make sure MCP server is running: cd pms_mcp_server && python -m src.sse_server")

# Check environment variables
print("\nEnvironment Variables:")
required_vars = ["OPENAI_API_KEY", "ASSEMBLYAI_API_KEY", "CARTESIA_API_KEY", "PMS_API_KEY"]
for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {'*' * 10}...")
    else:
        print(f"❌ {var}: Not set")

# Show agent instructions snippet
print("\nAgent Instructions Include:")
print("-"*60)
instructions = [
    "- Property Information Access (via MCP): get_customer_properties_context tool",
    "- Availability & Pricing Check (via MCP): check_property_availability_and_pricing tool",
    "",
    "ALWAYS use check_property_availability_and_pricing tool when:",
    "- Guest asks 'Is [property] available for [dates]?'",
    "- Guest wants to know pricing for specific dates",
    "- Guest asks 'How much would it cost for X nights?'",
    "- Guest mentions bringing pets (use include_pets parameter)",
]
for line in instructions:
    print(line)

print("\n" + "="*60)
print("Next Steps:")
print("1. Ensure MCP server is running in production container")
print("2. Add PMS_MCP_SERVER_URL to production environment")
print("3. Restart agent to load new instructions")
print("4. Test with availability questions like:")
print("   - 'Is the villa available next weekend?'")
print("   - 'How much for 5 nights in July with 4 guests?'")
print("   - 'Can we bring our dog?'")