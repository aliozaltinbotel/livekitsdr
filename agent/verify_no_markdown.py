#!/usr/bin/env python3
"""Verify no markdown formatting in agent instructions"""

import re

# Read the agent.py file
with open('agent.py', 'r') as f:
    content = f.read()

# Extract the instructions section
import_match = re.search(r'instructions=f"""(.+?)"""', content, re.DOTALL)
if import_match:
    instructions = import_match.group(1)
    
    # Check for markdown patterns
    markdown_patterns = [
        (r'\*\*[^*]+\*\*', 'Bold text (**text**)'),
        (r'\*[^*]+\*', 'Italic text (*text*)'),
        (r'#{1,6}\s', 'Headers (#, ##, ###)'),
        (r'`[^`]+`', 'Code blocks (`code`)'),
        (r'\[([^\]]+)\]\([^)]+\)', 'Links [text](url)'),
        (r'^\s*[-*+]\s', 'Bullet points (-, *, +)'),
        (r'^\s*\d+\.\s', 'Numbered lists'),
        (r'={3,}', 'Divider lines (===)'),
        (r'-{3,}', 'Divider lines (---)'),
        (r'→', 'Arrow symbols (→)'),
        (r'•', 'Bullet symbols (•)'),
    ]
    
    print("Checking for markdown formatting in agent instructions...")
    print("="*60)
    
    found_issues = False
    for pattern, description in markdown_patterns:
        matches = list(re.finditer(pattern, instructions, re.MULTILINE))
        if matches:
            found_issues = True
            print(f"\n❌ Found {description}: {len(matches)} occurrences")
            for i, match in enumerate(matches[:3]):  # Show first 3 examples
                line_num = instructions[:match.start()].count('\n') + 1
                print(f"   Line ~{line_num}: {match.group()}")
            if len(matches) > 3:
                print(f"   ... and {len(matches) - 3} more")
    
    if not found_issues:
        print("✅ No markdown formatting found in agent instructions!")
    else:
        print("\n⚠️  Some markdown formatting still present")
else:
    print("Could not find instructions in agent.py")