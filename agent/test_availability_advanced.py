#!/usr/bin/env python3
"""Test advanced availability and calendar endpoints"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

async def test_availability_endpoints():
    """Test various availability-related endpoints"""
    
    # Load environment variables
    load_dotenv('/Users/aliozaltin/Desktop/livekitsdr/agent/pms_mcp_server/.env')
    
    api_key = os.getenv("PMS_API_KEY")
    customer_id = os.getenv("PMS_CUSTOMER_ID", "ae0c85c5-7fa7-4e09-8a94-0df5da38e72e")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "customerId": customer_id,
        "Content-Type": "application/json"
    }
    
    property_id = "fde09fba-3a96-4705-a0c4-4bd264fb61da"
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    print("=" * 80)
    print("AVAILABILITY AND CALENDAR API TEST")
    print("=" * 80)
    
    async with aiohttp.ClientSession() as session:
        # 1. Try Reservation Search to see booked dates
        print("\n1. Testing GET /api/Reservation/Get - Check existing bookings")
        print("-" * 40)
        
        try:
            async with session.get(
                "https://pms.botel.ai/api/Reservation/Get",
                headers=headers,
                params={
                    "propertyId": property_id,
                    "pageSize": 100
                }
            ) as resp:
                print(f"Status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    print(f"Total Reservations: {data.get('totalCount', 0)}")
                    if data.get('items'):
                        print("\nReservations:")
                        for res in data['items'][:5]:  # Show first 5
                            print(f"- ID: {res.get('id')}")
                            print(f"  Check-in: {res.get('checkIn')}")
                            print(f"  Check-out: {res.get('checkOut')}")
                            print(f"  Status: {res.get('status')}")
                            print(f"  Total: {res.get('totalAmount')} {res.get('currency')}")
                else:
                    print(f"Error: {await resp.text()}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # 2. Try Calendar endpoint if exists
        print("\n\n2. Testing GET /api/Calendar/Get - Property calendar")
        print("-" * 40)
        
        try:
            async with session.get(
                "https://pms.botel.ai/api/Calendar/Get",
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
                    print(json.dumps(data, indent=2)[:500] + "..." if len(json.dumps(data)) > 500 else json.dumps(data, indent=2))
                else:
                    print(f"Error: {await resp.text()}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # 3. Try Availability endpoint
        print("\n\n3. Testing GET /api/Availability/Get")
        print("-" * 40)
        
        try:
            async with session.get(
                "https://pms.botel.ai/api/Availability/Get",
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
        
        # 4. Try to calculate pricing based on property settings
        print("\n\n4. Calculate pricing from property data")
        print("-" * 40)
        
        # Get property details with pricing
        try:
            async with session.get(
                "https://pms.botel.ai/api/Property/Get",
                headers=headers,
                params={"Id": property_id}
            ) as resp:
                if resp.status == 200:
                    prop_data = await resp.json()
                    pricing = prop_data.get('pricingSettings', {})
                    
                    print("Property Pricing Settings:")
                    print(f"- Base Price: {pricing.get('currency', 'EUR')} {pricing.get('basePrice', 0)}/night")
                    print(f"- Cleaning Fee: {pricing.get('currency', 'EUR')} {pricing.get('cleaningFee', 0)}")
                    print(f"- Security Deposit: {pricing.get('currency', 'EUR')} {pricing.get('securityDepositFee', 0)}")
                    print(f"- Pet Fee: {pricing.get('currency', 'EUR')} {pricing.get('petFee', 0)}")
                    print(f"- Extra Person Fee: {pricing.get('currency', 'EUR')} {pricing.get('extraPersonFee', 0)}")
                    print(f"- Weekend Base Price: {pricing.get('currency', 'EUR')} {pricing.get('weekendBasePrice', 0)}")
                    
                    # Calculate sample pricing
                    nights = 7
                    base_total = pricing.get('basePrice', 0) * nights
                    print(f"\nSample calculation for {nights} nights:")
                    print(f"- Accommodation: {pricing.get('currency', 'EUR')} {base_total}")
                    print(f"- Cleaning: {pricing.get('currency', 'EUR')} {pricing.get('cleaningFee', 0)}")
                    print(f"- Total: {pricing.get('currency', 'EUR')} {base_total + pricing.get('cleaningFee', 0)}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_availability_endpoints())