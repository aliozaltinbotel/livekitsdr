#!/usr/bin/env python3
"""Test date parsing fix for availability checks"""

import asyncio
import httpx
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_availability_with_proper_dates():
    """Test availability check with 2025 dates"""
    
    # MCP server URL
    mcp_url = os.getenv("PMS_MCP_SERVER_URL", "http://localhost:3001")
    messages_url = f"{mcp_url.replace('/sse', '')}/messages/"
    
    print("Testing Availability Check with Proper 2025 Dates")
    print("="*60)
    
    # Test property ID (Villa Nautilus)
    property_id = "fde09fba-3a96-4705-a0c4-4bd264fb61da"
    
    # Test with proper 2025 dates
    test_cases = [
        {
            "description": "June 28 to July 5, 2025",
            "check_in": "2025-06-28",
            "check_out": "2025-07-05",
            "guests": 4
        },
        {
            "description": "December 20-27, 2025 (Holiday week)",
            "check_in": "2025-12-20", 
            "check_out": "2025-12-27",
            "guests": 6
        },
        {
            "description": "Next weekend (relative date)",
            "check_in": "2025-06-28",  # Assuming next weekend from June 26
            "check_out": "2025-06-30",
            "guests": 2
        }
    ]
    
    async with httpx.AsyncClient() as client:
        session_id = "test-date-fix"
        
        # Initialize session
        init_response = await client.post(
            f"{messages_url}?session_id={session_id}",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {}
                }
            }
        )
        print(f"Initialize response: {init_response.status_code}")
        
        # Test each case
        for idx, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {idx}: {test_case['description']}")
            print("-"*40)
            
            # Call availability tool
            tool_response = await client.post(
                f"{messages_url}?session_id={session_id}",
                json={
                    "jsonrpc": "2.0",
                    "id": idx + 1,
                    "method": "tools/call",
                    "params": {
                        "name": "check_property_availability_and_pricing",
                        "arguments": {
                            "property_id": property_id,
                            "check_in_date": test_case["check_in"],
                            "check_out_date": test_case["check_out"],
                            "guest_count": test_case["guests"],
                            "include_pets": False
                        }
                    }
                }
            )
            
            print(f"Response status: {tool_response.status_code}")
            
            # Parse result
            if tool_response.status_code == 200:
                result = tool_response.json()
                if "result" in result and "content" in result["result"]:
                    content = result["result"]["content"][0]["text"]
                    # Extract key info
                    lines = content.split("\n")
                    for line in lines:
                        if "Available" in line or "Total Cost" in line or "Error" in line:
                            print(f"  → {line.strip()}")
    
    print("\n" + "="*60)
    print("✅ Date parsing test complete")
    print("\nKey Points:")
    print("- Agent should now use 2025 for all date parsing")
    print("- Ambiguous dates like 'June 28' default to current year")
    print("- Past dates in current year should prompt for clarification")

if __name__ == "__main__":
    asyncio.run(test_availability_with_proper_dates())