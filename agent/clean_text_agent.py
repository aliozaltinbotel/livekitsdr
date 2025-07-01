"""
Clean Text Agent for LiveKit
Strips markdown formatting before TTS to prevent reading asterisks and other formatting
"""

import re
from typing import AsyncIterable
from livekit.agents import llm
from livekit.agents.voice import Agent


class CleanTextAssistant(Agent):
    """
    Custom Assistant that cleans markdown formatting from text before TTS
    """
    
    async def transcription_node(
        self, 
        text: AsyncIterable[str], 
        model_settings=None
    ) -> AsyncIterable[str]:
        """
        Override the transcription node to clean markdown formatting
        before text is sent to TTS
        
        This node is part of the forwarding path for agent transcriptions
        and can be used to adjust or post-process text coming from an LLM
        """
        async for chunk in text:
            # Remove bold/italic markers (**text** or __text__)
            cleaned = re.sub(r'\*{1,2}([^\*]+)\*{1,2}', r'\1', chunk)
            cleaned = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', cleaned)
            
            # Remove inline code backticks
            cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)
            
            # Remove strikethrough
            cleaned = re.sub(r'~{2}([^~]+)~{2}', r'\1', cleaned)
            
            # Remove headers (# Header, ## Header, etc.)
            cleaned = re.sub(r'^#{1,6}\s+', '', cleaned, flags=re.MULTILINE)
            
            # Remove bullet points
            cleaned = re.sub(r'^[\-\*\+]\s+', '', cleaned, flags=re.MULTILINE)
            
            # Remove numbered lists
            cleaned = re.sub(r'^\d+\.\s+', '', cleaned, flags=re.MULTILINE)
            
            # Remove links [text](url)
            cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)
            
            # Remove horizontal rules
            cleaned = re.sub(r'^[\-\*_]{3,}$', '', cleaned, flags=re.MULTILINE)
            
            # Remove blockquotes
            cleaned = re.sub(r'^>\s+', '', cleaned, flags=re.MULTILINE)
            
            # Clean up multiple spaces
            cleaned = re.sub(r' {2,}', ' ', cleaned)
            
            yield cleaned