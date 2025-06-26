#!/usr/bin/env python3
"""Test script to simulate availability questions for the agent"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test scenarios for the agent
test_scenarios = [
    {
        "name": "Basic Availability Check",
        "questions": [
            "Is the villa available from July 15th to 20th?",
            "4 adults",
        ],
        "expected": "Should return availability status and pricing for 5 nights"
    },
    {
        "name": "Check with Pets",
        "questions": [
            "Can we bring our dog for next weekend?",
            "The villa, 2 people",
        ],
        "expected": "Should calculate weekend dates and include pet fee"
    },
    {
        "name": "Price Check Only",
        "questions": [
            "How much would it cost for 7 nights in August?",
            "August 1st to 8th, 6 guests",
        ],
        "expected": "Should provide pricing breakdown for 7 nights with 6 guests"
    },
    {
        "name": "Too Many Guests",
        "questions": [
            "Do you have availability for 10 people?",
            "Next month, any week",
        ],
        "expected": "Should explain max occupancy is 8"
    },
    {
        "name": "Vague Dates",
        "questions": [
            "Is the place free this summer?",
            "Sometime in July, maybe 3-4 nights, family of 5",
        ],
        "expected": "Should ask for specific dates"
    }
]

def print_scenario(scenario):
    """Print test scenario details"""
    print("\n" + "="*80)
    print(f"SCENARIO: {scenario['name']}")
    print("="*80)
    print("Questions:")
    for i, q in enumerate(scenario['questions'], 1):
        print(f"  {i}. {q}")
    print(f"\nExpected: {scenario['expected']}")
    print("-"*80)

async def main():
    """Run test scenarios"""
    print("AGENT AVAILABILITY & PRICING TEST SCENARIOS")
    print("="*80)
    print("These scenarios test how the agent should handle availability and pricing questions.")
    print("The agent should use the check_property_availability_and_pricing MCP tool.")
    
    # Show current date for reference
    print(f"\nCurrent date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Next weekend: {(datetime.now() + timedelta(days=(5-datetime.now().weekday())%7)).strftime('%Y-%m-%d')}")
    
    # Print all scenarios
    for scenario in test_scenarios:
        print_scenario(scenario)
    
    print("\n" + "="*80)
    print("IMPLEMENTATION NOTES:")
    print("="*80)
    print("1. Agent should naturally collect required information:")
    print("   - Property ID (from context)")
    print("   - Check-in and check-out dates") 
    print("   - Number of guests")
    print("   - Pet information if mentioned")
    print("\n2. Date parsing should handle:")
    print("   - Specific dates (July 15th)")
    print("   - Relative dates (next weekend)")
    print("   - Date ranges (August 1st to 8th)")
    print("\n3. Response should be conversational:")
    print("   - No technical jargon")
    print("   - Clear pricing breakdowns")
    print("   - Helpful alternatives if not available")

if __name__ == "__main__":
    asyncio.run(main())