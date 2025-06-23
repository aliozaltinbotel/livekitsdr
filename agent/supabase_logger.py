"""
Enhanced Supabase logger for comprehensive session and conversation tracking
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class SupabaseLogger:
    """Handles all Supabase logging for sessions and conversations"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.current_session_id: Optional[str] = None
        self.session_data: Dict[str, Any] = {}
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client if credentials are available"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if supabase_url and supabase_key:
            try:
                self.client = create_client(supabase_url, supabase_key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
        else:
            logger.warning("Supabase credentials not found. Logging disabled.")
    
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
    
    async def log_message(self, room_id: str, participant_id: str, role: str, message: str, 
                         confidence: Optional[float] = None, metadata: Optional[Dict] = None):
        """Log a conversation message"""
        if not self.client:
            return
        
        try:
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
    
    async def update_session_data(self, room_id: str, data: Dict[str, Any]):
        """Update session with collected user data"""
        if not self.client:
            logger.warning("No Supabase client available for update")
            return
        
        # Store data locally
        self.session_data.update(data)
        
        try:
            # Update in database
            update_data = {
                'updated_at': datetime.utcnow().isoformat(),
                **data
            }
            
            logger.info(f"Updating session {room_id} with data: {update_data}")
            
            result = await asyncio.to_thread(
                lambda: self.client.table('sessions').update(update_data).eq('session_id', room_id).execute()
            )
            
            if result.data and len(result.data) > 0:
                logger.info(f"Session data updated successfully for {room_id}: {data}")
                logger.info(f"Updated rows: {len(result.data)}")
            else:
                logger.warning(f"No rows updated for session {room_id}")
                # Try to create session if it doesn't exist
                logger.info(f"Attempting to create session {room_id} with data")
                session_data = {
                    'session_id': room_id,
                    'started_at': datetime.utcnow().isoformat(),
                    'status': 'active',
                    **data
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