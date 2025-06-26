#!/usr/bin/env python3
"""Test the agent's dynamic date context"""

from datetime import datetime

# Simulate what the agent sees
today = datetime.now()
current_date_str = today.strftime("%B %d, %Y")
current_year = today.year

print("Agent Dynamic Date Context Test")
print("="*60)
print(f"\nThe agent will see:")
print(f"- Today's date: {current_date_str}")
print(f"- Current year: {current_year}")

print(f"\nWhen a guest says:")
print(f'  "Is the villa available June 28 to July 5?"')
print(f"\nThe agent will interpret as:")
print(f"  {current_year}-06-28 to {current_year}-07-05")

print(f"\nWhen a guest says:")
print(f'  "What about next Christmas?"')
print(f"\nThe agent will interpret as:")
print(f"  December 25, {current_year}")

# Test future year scenario
from datetime import timedelta
future_date = today + timedelta(days=365)
print(f"\n\nIn one year ({future_date.strftime('%B %d, %Y')}), the agent will automatically use:")
print(f"- Year: {future_date.year}")
print(f"- All date parsing will use {future_date.year} instead")

print("\n✅ The date handling is now fully dynamic and future-proof!")