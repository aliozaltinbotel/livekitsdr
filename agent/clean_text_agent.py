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
        Override the say method to handle text chunking for long responses
        """
        # Don't clean markdown here - let the TTS wrapper handle it
        # to avoid double cleaning
        
        logger.info(f"Say method called with text: '{text[:100]}...' (length: {len(text)})")
        
        # Check if text is too long and needs chunking
        # Cartesia has a limit, let's chunk at 500 characters for natural breaks
        if len(text) > 500:
            logger.info(f"Text too long ({len(text)} chars), chunking for better TTS delivery")
            return await self._say_chunked(text, *args, **kwargs)
        
        # Call parent's say method with original text
        return await super().say(text, *args, **kwargs)
    
    async def _say_chunked(self, text: str, *args, **kwargs):
        """
        Break long text into smaller chunks for TTS
        """
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        chunks = []
        
        for sentence in sentences:
            # If adding this sentence would exceed limit, save current chunk
            if current_chunk and len(current_chunk) + len(sentence) > 400:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Split text into {len(chunks)} chunks for TTS")
        
        # Speak each chunk
        for i, chunk in enumerate(chunks):
            logger.info(f"Speaking chunk {i+1}/{len(chunks)}: {chunk[:50]}...")
            await super().say(chunk, *args, **kwargs)
            # Small pause between chunks for natural flow
            if i < len(chunks) - 1:
                await super().say("...", *args, **kwargs)
    
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