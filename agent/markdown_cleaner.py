"""
Markdown cleaner utility for removing markdown formatting from text
"""

import re


def clean_markdown_for_voice(text: str) -> str:
    """
    Remove markdown formatting from text to prevent TTS from reading formatting characters
    """
    if not text:
        return text
    
    # Remove bold markers (**text** or __text__)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    
    # Remove italic markers (*text* or _text_)
    # Be careful not to remove single asterisks that might be bullet points
    text = re.sub(r'(?<!\*)\*(?!\*)([^\*\n]+)\*(?!\*)', r'\1', text)
    text = re.sub(r'(?<!_)_(?!_)([^_\n]+)_(?!_)', r'\1', text)
    
    # Remove inline code backticks
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove headers (# Header, ## Header, etc.)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove strikethrough
    text = re.sub(r'~~([^~]+)~~', r'\1', text)
    
    # Remove links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove bullet points and numbered lists
    text = re.sub(r'^[\-\*\+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules
    text = re.sub(r'^[\-\*_]{3,}$', '', text, flags=re.MULTILINE)
    
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # Remove code blocks
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    
    # Clean up multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text