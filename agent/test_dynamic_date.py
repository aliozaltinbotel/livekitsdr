#!/usr/bin/env python3
"""Test dynamic date in agent instructions"""

from datetime import datetime

# Test the date formatting
today = datetime.now()
current_date_str = today.strftime("%B %d, %Y")
current_year = today.year

print("Dynamic Date Test")
print("="*50)
print(f"Today's date: {current_date_str}")
print(f"Current year: {current_year}")
print(f"Previous years: {current_year-2}, {current_year-1}")
print("\nExample instructions snippet:")
print(f"Current Context: Today's date is {current_date_str}. Always use current year ({current_year}) when parsing dates.")
print(f"\nDate parsing example: July 4th to 8th → {current_year}-07-04 to {current_year}-07-08")