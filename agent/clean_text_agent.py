"""
Clean Text Agent for LiveKit
Strips markdown formatting before TTS to prevent reading asterisks and other formatting
"""

import re
import logging
from typing import AsyncIterable
from livekit.agents.voice import Agent

logger = logging.getLogger(__name__)


class CleanTextAssistant(Agent):
    """
    Custom Assistant that cleans markdown formatting from text before TTS
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("CleanTextAssistant initialized with markdown stripping")
    
    async def say(self, text: str, *args, **kwargs):
        """
        Override the say method to clean markdown before speaking
        """
        # Clean markdown from the text
        cleaned_text = self._clean_markdown(text)
        
        # Log if we made changes
        if text != cleaned_text:
            logger.info(f"Cleaned markdown before TTS: '{text[:50]}...' -> '{cleaned_text[:50]}...'")
        
        # Call parent's say method with cleaned text
        return await super().say(cleaned_text, *args, **kwargs)
    
    def _clean_markdown(self, text: str) -> str:
        """
        Remove markdown formatting from text
        """
        # Remove bold markers (**text** or __text__)
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        
        # Remove italic markers (*text* or _text_)
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        
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
        
        # Clean up multiple spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()