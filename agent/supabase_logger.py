"""
Enhanced Supabase logger for comprehensive session and conversation tracking
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
import logging
from supabase import create_client, Client
import httpx
from functools import wraps
import time

logger = logging.getLogger(__name__)

def retry_on_error(max_retries=3, delay=1.0):
    """Decorator to retry failed operations"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed. Last error: {e}")
            raise last_error
        return wrapper
    return decorator

class SupabaseLogger:
    """Handles all Supabase logging for sessions and conversations"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.current_session_id: Optional[str] = None
        self.session_data: Dict[str, Any] = {}
        self._http_client: Optional[httpx.AsyncClient] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client if credentials are available"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if supabase_url and supabase_key and not supabase_url.startswith("https://<your-project>"):
            try:
                # Create custom HTTP client with proper settings
                transport = httpx.HTTPTransport(
                    retries=3,
                    http2=True,
                    limits=httpx.Limits(
                        max_keepalive_connections=5,
                        max_connections=10,
                        keepalive_expiry=30.0
                    )
                )
                
                # Create async client for better connection management
                self._http_client = httpx.AsyncClient(
                    transport=transport,
                    timeout=httpx.Timeout(30.0)
                )
                
                self.client = create_client(supabase_url, supabase_key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
        else:
            logger.info("Supabase credentials not found. Logging disabled.")
            self.client = None
    
    async def start_session(self, room_id: str, job_id: str, participant_id: str) -> Optional[str]:
        """Start a new session and return session ID"""
        if not self.client:
            return None
        
        try:
            self.current_session_id = room_id
            session_data = {
                'session_id': room_id,
                'job_id': job_id,
                'participant_id': participant_id,
                'started_at': datetime.utcnow().isoformat(),
                'status': 'active',
                'agent_version': 'jamie-v1'
            }
            
            result = await asyncio.to_thread(
                lambda: self.client.table('sessions').insert(session_data).execute()
            )
            logger.info(f"Session started: {room_id}")
            
            # Log system message about session start
            await self.log_message(
                room_id=room_id,
                participant_id=participant_id,
                role="system",
                message="Session started with Jamie AI assistant"
            )
            
            return room_id
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return None
    
    async def end_session(self, room_id: str, status: str = 'completed'):
        """End a session and update its status"""
        if not self.client or not room_id:
            logger.warning(f"Cannot end session: client={bool(self.client)}, room_id={room_id}")
            return
        
        try:
            update_data = {
                'ended_at': datetime.utcnow().isoformat(),
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Add any collected user data
            if self.session_data:
                logger.info(f"Adding collected session data to final update: {self.session_data}")
                update_data.update(self.session_data)
            
            logger.info(f"Ending session {room_id} with update data: {update_data}")
            
            result = await asyncio.to_thread(
                lambda: self.client.table('sessions').update(update_data).eq('session_id', room_id).execute()
            )
            
            if result.data:
                logger.info(f"Session ended successfully: {room_id} with status: {status}")
            else:
                logger.warning(f"No session found to end: {room_id}")
            
            # Log system message about session end
            await self.log_message(
                room_id=room_id,
                participant_id="system",
                role="system",
                message=f"Session ended with status: {status}"
            )
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
    
    @retry_on_error(max_retries=2, delay=0.5)
    async def log_message(self, room_id: str, participant_id: str, role: str, message: str, 
                         confidence: Optional[float] = None, metadata: Optional[Dict] = None):
        """Log a conversation message"""
        if not self.client:
            return
        
        try:
            # Ensure message is not too long for JSON
            if len(message) > 10000:
                message = message[:10000] + "... (truncated)"
            
            message_data = {
                'session_id': room_id,
                'room_id': room_id,
                'participant_id': participant_id,
                'role': role,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if confidence is not None:
                message_data['confidence'] = confidence
            
            if metadata:
                message_data['metadata'] = metadata
            
            await asyncio.to_thread(
                lambda: self.client.table('conversations').insert(message_data).execute()
            )
            
        except Exception as e:
            logger.error(f"Error logging message: {e}")
    
    @retry_on_error(max_retries=2, delay=0.5)
    async def update_session_data(self, room_id: str, data: Dict[str, Any]):
        """Update session with collected user data"""
        if not self.client:
            logger.warning("No Supabase client available for update")
            return
        
        # Validate and clean data
        cleaned_data = {}
        for key, value in data.items():
            if value is not None and value != "":
                # Ensure strings are not too long
                if isinstance(value, str) and len(value) > 1000:
                    value = value[:1000]
                cleaned_data[key] = value
        
        # Store data locally
        self.session_data.update(cleaned_data)
        
        try:
            # Update in database
            update_data = {
                'updated_at': datetime.utcnow().isoformat(),
                **cleaned_data
            }
            
            logger.info(f"Updating session {room_id} with data: {update_data}")
            
            result = await asyncio.to_thread(
                lambda: self.client.table('sessions').update(update_data).eq('session_id', room_id).execute()
            )
            
            if result.data and len(result.data) > 0:
                logger.info(f"Session data updated successfully for {room_id}: {cleaned_data}")
                logger.info(f"Updated rows: {len(result.data)}")
            else:
                logger.warning(f"No rows updated for session {room_id}")
                # Try to create session if it doesn't exist
                logger.info(f"Attempting to create session {room_id} with data")
                session_data = {
                    'session_id': room_id,
                    'started_at': datetime.utcnow().isoformat(),
                    'status': 'active',
                    **cleaned_data
                }
                create_result = await asyncio.to_thread(
                    lambda: self.client.table('sessions').upsert(session_data).execute()
                )
                if create_result.data:
                    logger.info(f"Session created/updated via upsert: {room_id}")
                
        except Exception as e:
            logger.error(f"Error updating session data for {room_id}: {e}")
            logger.error(f"Update data was: {update_data}")
    
    async def log_tool_call(self, room_id: str, tool_name: str, parameters: Dict, 
                           result: str, success: bool = True, error_message: Optional[str] = None):
        """Log a tool call (calendar operations, etc)"""
        if not self.client:
            return
        
        try:
            tool_data = {
                'session_id': room_id,
                'tool_name': tool_name,
                'parameters': parameters,
                'result': result,
                'success': success,
                'error_message': error_message,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await asyncio.to_thread(
                lambda: self.client.table('tool_calls').insert(tool_data).execute()
            )
            logger.info(f"Tool call logged: {tool_name}")
            
        except Exception as e:
            logger.error(f"Error logging tool call: {e}")
    
    async def mark_demo_scheduled(self, room_id: str, demo_time: str, timezone: str):
        """Mark that a demo was successfully scheduled"""
        data = {
            'demo_scheduled': True,
            'demo_time': demo_time,
            'demo_timezone': timezone
        }
        logger.info(f"Marking demo scheduled for session {room_id}: {data}")
        await self.update_session_data(room_id, data)

# Global instance
supabase_logger = SupabaseLogger()