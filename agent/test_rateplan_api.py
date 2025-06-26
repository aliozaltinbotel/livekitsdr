#!/usr/bin/env python3
"""Test RatePlan API endpoints to understand data structure"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

async def test_rateplan_apis():
    """Test RatePlan APIs to understand the data structure"""
    
    # Load environment variables
    load_dotenv('/Users/aliozaltin/Desktop/livekitsdr/agent/pms_mcp_server/.env')
    
    api_key = os.getenv("PMS_API_KEY")
    customer_id = os.getenv("PMS_CUSTOMER_ID", "ae0c85c5-7fa7-4e09-8a94-0df5da38e72e")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "customerId": customer_id,
        "Content-Type": "application/json"
    }
    
    # Test property ID from earlier
    property_id = "fde09fba-3a96-4705-a0c4-4bd264fb61da"
    
    # Calculate date range (next 7 days from today)
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    print("=" * 80)
    print("RATEPLAN API TEST")
    print(f"Property ID: {property_id}")
    print(f"Date Range: {start_date} to {end_date}")
    print("=" * 80)
    
    async with aiohttp.ClientSession() as session:
        # 1. Get all rate plans for the property
        print("\n1. Testing GET /api/RatePlan/Get")
        print("-" * 40)
        
        try:
            async with session.get(
                "https://pms.botel.ai/api/RatePlan/Get",
                headers=headers,
                params={"propertyId": property_id}
            ) as resp:
                print(f"Status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    print("Response:")
                    print(json.dumps(data, indent=2))
                else:
                    print(f"Error: {await resp.text()}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # 2. Check availability and pricing
        print("\n\n2. Testing GET /api/RatePlan/CheckAvailability")
        print("-" * 40)
        
        try:
            async with session.get(
                "https://pms.botel.ai/api/RatePlan/CheckAvailability",
                headers=headers,
                params={
                    "propertyId": property_id,
                    "startDate": start_date,
                    "endDate": end_date,
                    "guestCount": 4
                }
            ) as resp:
                print(f"Status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    print("Response:")
                    print(json.dumps(data, indent=2))
                else:
                    print(f"Error: {await resp.text()}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # 3. Search rate plans
        print("\n\n3. Testing GET /api/RatePlan/Search")
        print("-" * 40)
        
        try:
            async with session.get(
                "https://pms.botel.ai/api/RatePlan/Search",
                headers=headers,
                params={
                    "startDate": start_date,
                    "endDate": end_date,
                    "guestCount": 4
                }
            ) as resp:
                print(f"Status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    print("Response:")
                    print(json.dumps(data, indent=2))
                else:
                    print(f"Error: {await resp.text()}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # 4. Also test Property availability endpoint
        print("\n\n4. Testing GET /api/Property/GetAvailability")
        print("-" * 40)
        
        try:
            async with session.get(
                "https://pms.botel.ai/api/Property/GetAvailability",
                headers=headers,
                params={
                    "propertyId": property_id,
                    "startDate": start_date,
                    "endDate": end_date
                }
            ) as resp:
                print(f"Status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    print("Response:")
                    print(json.dumps(data, indent=2))
                else:
                    print(f"Error: {await resp.text()}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_rateplan_apis())