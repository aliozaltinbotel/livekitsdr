"""
TTS Wrapper that cleans markdown before synthesis
"""

import logging
from typing import Optional, Union, AsyncIterator
from livekit.plugins import cartesia
from livekit import rtc
from markdown_cleaner import clean_markdown_for_voice

logger = logging.getLogger(__name__)


class CleanTTSWrapper:
    """
    Wrapper for Cartesia TTS that cleans markdown formatting before synthesis
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "sonic-turbo",
        voice: str = "86e30c1d-714b-4074-a1f2-1cb6b552fb49",
        language: str = "en",
        speed: float = 0.0,
        sample_rate: int = 24000
    ):
        # Create the underlying Cartesia TTS instance
        self._tts = cartesia.TTS(
            api_key=api_key,
            model=model,
            voice=voice,
            language=language,
            speed=speed,
            sample_rate=sample_rate
        )
        self._sample_rate = sample_rate
        logger.info("CleanTTSWrapper initialized with markdown stripping")
    
    async def synthesize(
        self,
        text: str,
        *,
        sample_rate: int = 24000,
        num_channels: int = 1
    ) -> rtc.AudioFrame:
        """
        Synthesize speech from text after cleaning markdown
        """
        # Clean markdown from text
        cleaned_text = clean_markdown_for_voice(text)
        
        # Log if we made changes
        if text != cleaned_text:
            logger.info(f"Cleaned markdown before TTS: '{text[:50]}...' -> '{cleaned_text[:50]}...'")
        
        # Call the underlying TTS synthesize method
        return await self._tts.synthesize(
            cleaned_text,
            sample_rate=sample_rate,
            num_channels=num_channels
        )
    
    def stream(
        self,
        *,
        conn_options: Optional[dict] = None
    ):
        """
        Create a streaming TTS session that cleans markdown
        
        Note: sample_rate and num_channels are configured when creating the TTS instance,
        not when creating a stream.
        """
        # Return a wrapped stream that cleans text before synthesis
        class CleanStreamWrapper:
            def __init__(self, tts_stream):
                self._stream = tts_stream
            
            async def __aenter__(self):
                """Enter the async context manager"""
                await self._stream.__aenter__()
                return self
                
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                """Exit the async context manager"""
                return await self._stream.__aexit__(exc_type, exc_val, exc_tb)
            
            def push_text(self, text: str) -> None:
                """Push cleaned text to the stream"""
                cleaned_text = clean_markdown_for_voice(text)
                if text != cleaned_text:
                    logger.debug(f"Stream: Cleaned markdown: '{text}' -> '{cleaned_text}'")
                self._stream.push_text(cleaned_text)
            
            async def push_frame(self, frame: Optional[rtc.AudioFrame]) -> None:
                """Push audio frame to the stream"""
                await self._stream.push_frame(frame)
            
            async def aclose(self) -> None:
                """Close the stream"""
                await self._stream.aclose()
            
            def __aiter__(self):
                return self._stream.__aiter__()
            
            async def __anext__(self):
                return await self._stream.__anext__()
        
        # Create the underlying stream
        # Only pass conn_options if provided
        if conn_options is not None:
            underlying_stream = self._tts.stream(conn_options=conn_options)
        else:
            underlying_stream = self._tts.stream()
                
        return CleanStreamWrapper(underlying_stream)
    
    # Forward any other attributes/methods to the underlying TTS
    def __getattr__(self, name):
        return getattr(self._tts, name)