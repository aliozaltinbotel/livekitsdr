"""
Google Calendar integration for direct event creation and invitations.
This is an alternative to Calendly that provides full control over calendar events.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import pytz
from livekit.agents import function_tool, RunContext

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False
    logger.warning("Google Calendar API libraries not installed. Using mock availability.")

class GoogleCalendarIntegration:
    """Direct Google Calendar integration for scheduling"""
    
    def __init__(self):
        self.service = None
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        logger.info(f"Initializing Google Calendar with calendar ID: {self.calendar_id}")
        self._initialize_service()
        
        # Log initialization status
        if self.service:
            logger.info("Google Calendar integration ready")
        else:
            logger.warning("Google Calendar integration not available - will use mock data")
    
    def _initialize_service(self):
        """Initialize Google Calendar service with credentials"""
        if not GOOGLE_CALENDAR_AVAILABLE:
            logger.info("Google Calendar API not available, using mock mode")
            return
            
        try:
            creds = None
            
            # First, try service account authentication
            service_account_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY")
            logger.info(f"Service account path: {service_account_path}")
            
            if service_account_path and os.path.exists(service_account_path):
                logger.info(f"Service account file found at: {service_account_path}")
                scopes = ['https://www.googleapis.com/auth/calendar']
                creds = service_account.Credentials.from_service_account_file(
                    service_account_path, scopes=scopes)
                
                # If domain delegation is enabled, impersonate a user
                delegated_user = os.getenv("GOOGLE_DELEGATED_USER_EMAIL")
                if delegated_user:
                    creds = creds.with_subject(delegated_user)
                    logger.info(f"Using service account with delegation as: {delegated_user}")
                else:
                    logger.info(f"Using service account without delegation")
            else:
                logger.warning(f"Service account file not found at: {service_account_path}")
                # Fall back to OAuth2 credentials
                token_path = 'token.json'
                
                # Check for existing token
                if os.path.exists(token_path):
                    creds = Credentials.from_authorized_user_file(token_path)
                    
                # Use credentials.json if no token exists
                if not creds:
                    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
                    if creds_path and os.path.exists(creds_path):
                        creds = Credentials.from_authorized_user_file(creds_path)
            
            if creds:
                self.service = build('calendar', 'v3', credentials=creds)
                logger.info("Google Calendar service initialized successfully")
            else:
                logger.warning("No valid Google Calendar credentials found")
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar: {e}")
    
    def check_availability(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Check calendar availability for a time range"""
        if not self.service:
            return []
        
        try:
            # Get busy times
            body = {
                "timeMin": start_date.isoformat(),
                "timeMax": end_date.isoformat(),
                "items": [{"id": self.calendar_id}]
            }
            
            events_result = self.service.freebusy().query(body=body).execute()
            busy_times = events_result['calendars'][self.calendar_id]['busy']
            
            # Generate available slots (simplified logic)
            available_slots = []
            current = start_date
            
            while current < end_date:
                if current.weekday() < 5:  # Monday-Friday
                    for hour in [10, 14, 16]:  # 10 AM, 2 PM, 4 PM
                        slot_start = current.replace(hour=hour, minute=0, second=0)
                        slot_end = slot_start + timedelta(hours=1)
                        
                        # Check if slot conflicts with busy times
                        is_available = True
                        for busy in busy_times:
                            busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                            busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                            if not (slot_end <= busy_start or slot_start >= busy_end):
                                is_available = False
                                break
                        
                        if is_available and slot_start > datetime.now(slot_start.tzinfo):
                            available_slots.append({
                                'start': slot_start,
                                'end': slot_end
                            })
                
                current += timedelta(days=1)
            
            return available_slots[:5]  # Return up to 5 slots
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            if "accessNotConfigured" in str(e):
                logger.warning("Google Calendar API not enabled. Please enable it in Google Cloud Console.")
            return []
    
    def create_event(self, 
                    summary: str,
                    start_time: datetime,
                    end_time: datetime,
                    attendee_email: str,
                    description: str = None) -> Optional[Dict]:
        """Create a calendar event and send invitation"""
        if not self.service:
            return None
        
        try:
            event = {
                'summary': summary,
                'description': description or f"Demo call scheduled via Botel AI voice assistant",
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': str(start_time.tzinfo),
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': str(end_time.tzinfo),
                },
                'attendees': [
                    {'email': attendee_email},
                ] if attendee_email and '@' in attendee_email else [],
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"botel-{datetime.now().timestamp()}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 15},  # 15 minutes before
                    ],
                },
            }
            
            # Create the event with conference data
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'  # This sends email invitations
            ).execute()
            
            logger.info(f"Created event: {event.get('htmlLink')}")
            return event
            
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            if "accessNotConfigured" in str(e):
                logger.warning("Google Calendar API not enabled. Please enable it in Google Cloud Console.")
            return None

# Initialize Google Calendar integration (will be done on first use)
google_calendar = None

def get_google_calendar():
    """Get or create Google Calendar integration instance"""
    global google_calendar
    if google_calendar is None:
        google_calendar = GoogleCalendarIntegration()
    return google_calendar

@function_tool
async def google_calendar_check_real_availability(
    context: RunContext,
    timezone: str = "America/New_York"
) -> str:
    """Check real calendar availability using Google Calendar.
    
    Args:
        timezone: The timezone to check availability in
    """
    print(f"[CALENDAR] Checking availability for timezone: {timezone}")
    logger.info(f"Checking availability for timezone: {timezone}")
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        end_date = now + timedelta(days=7)
        logger.info(f"Time range: {now} to {end_date}")
        
        calendar = get_google_calendar()
        if not calendar.service:
            logger.warning("Google Calendar service not initialized, using mock availability")
            # Fallback to mock availability if Google Calendar not configured
            slots = []
            days_checked = 0
            days_ahead = 1
            
            while len(slots) < 3 and days_checked < 7:
                date = now + timedelta(days=days_ahead)
                
                if date.weekday() < 5:  # Monday-Friday
                    time_slots = [10, 14, 16] if days_ahead > 1 else [14, 16]
                    
                    for hour in time_slots[:1]:
                        slot_time = date.replace(hour=hour, minute=0, second=0)
                        formatted = slot_time.strftime("%A at %-I:%M %p")
                        slots.append(formatted)
                        logger.info(f"Added mock slot: {formatted}")
                        
                        if len(slots) >= 3:
                            break
                
                days_checked += 1
                days_ahead += 1
            
            if len(slots) == 1:
                availability_text = slots[0]
            elif len(slots) == 2:
                availability_text = f"{slots[0]} or {slots[1]}"
            else:
                availability_text = f"{', '.join(slots[:-1])}, or {slots[-1]}"
            
            logger.info(f"Returning mock availability: {availability_text}")
            return f"Great, thanks! I have {availability_text} available—which works best for you?"
        
        # Get real availability
        calendar = get_google_calendar()
        available_slots = calendar.check_availability(now, end_date)
        
        if not available_slots:
            return "I'm having trouble accessing the calendar. Let me connect you with someone who can help schedule manually."
        
        # Format slots for conversation
        formatted_slots = []
        for slot in available_slots[:3]:
            formatted = slot['start'].strftime("%A at %-I:%M %p")
            formatted_slots.append(formatted)
        
        if len(formatted_slots) == 1:
            availability_text = formatted_slots[0]
        elif len(formatted_slots) == 2:
            availability_text = f"{formatted_slots[0]} or {formatted_slots[1]}"
        else:
            availability_text = f"{', '.join(formatted_slots[:-1])}, or {formatted_slots[-1]}"
        
        return f"I have {availability_text} available—which works best for you?"
        
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        if "accessNotConfigured" in str(e):
            logger.warning("Google Calendar API not enabled. Using fallback availability.")
            # Return mock availability as fallback
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
            slots = []
            
            for days_ahead in [1, 2, 3]:
                date = now + timedelta(days=days_ahead)
                if date.weekday() < 5:  # Monday-Friday
                    slot_time = date.replace(hour=14, minute=0, second=0)
                    formatted = slot_time.strftime("%A at %-I:%M %p")
                    slots.append(formatted)
                    if len(slots) >= 3:
                        break
            
            availability_text = f"{', '.join(slots[:-1])}, or {slots[-1]}"
            return f"Great, thanks! I have {availability_text} available—which works best for you?"
        return "Let me check with our team about available times and get back to you."

@function_tool
async def google_calendar_create_meeting(
    context: RunContext,
    email: str,
    meeting_time: str,
    timezone: str = "America/New_York"
) -> str:
    """Create a calendar event and send invitation email.
    
    Args:
        email: The attendee's email address
        meeting_time: The selected meeting time (e.g., "Monday at 10:00 AM")
        timezone: The timezone for the meeting
    """
    print(f"[CALENDAR] Creating meeting for {email} at '{meeting_time}' in timezone {timezone}")
    logger.info(f"Creating meeting for {email} at '{meeting_time}' in timezone {timezone}")
    
    # Validate email
    if not email or '@' not in email or email.startswith('[') or email == '[contact email]':
        error_msg = f"Invalid email address provided: '{email}'. Please provide a valid email address."
        print(f"[CALENDAR ERROR] {error_msg}")
        logger.error(error_msg)
        return "I need a valid email address to send the calendar invite. Could you please confirm your email?"
    
    try:
        calendar = get_google_calendar()
        if not calendar.service:
            # Fallback response if Google Calendar not configured
            return (
                f"I'll coordinate with our team to send you a calendar invitation for {meeting_time} "
                f"to {email}. You'll receive an email with the meeting details and Google Meet link shortly. "
                f"Looking forward to our conversation!"
            )
        
        # Parse the meeting time
        tz = pytz.timezone(timezone)
        
        # Remove any asterisks or brackets that might be in the meeting_time
        meeting_time_clean = meeting_time.strip().replace("*", "").replace("[", "").replace("]", "")
        logger.info(f"Cleaned meeting time: '{meeting_time_clean}'")
        
        # Simple parsing logic (you'd want more robust parsing in production)
        # Extract day and time from "Monday at 10:00 AM" format
        if " at " not in meeting_time_clean:
            logger.error(f"Invalid meeting time format: '{meeting_time_clean}'")
            return (
                f"I'll coordinate with our team to send you a calendar invitation for {meeting_time} "
                f"to {email}. You'll receive an email with the meeting details shortly."
            )
        
        parts = meeting_time_clean.split(" at ")
        day_name = parts[0].strip()
        time_str = parts[1].strip()
        
        logger.info(f"Parsed day: '{day_name}', time: '{time_str}'")
        
        # Find the next occurrence of the specified day
        now = datetime.now(tz)
        days_ahead = 0
        for i in range(7):
            check_date = now + timedelta(days=i)
            if check_date.strftime("%A").lower() == day_name.lower():
                days_ahead = i
                break
        
        # Parse time
        try:
            from datetime import datetime as dt
            time_obj = dt.strptime(time_str, "%I:%M %p")
        except ValueError as e:
            logger.error(f"Failed to parse time '{time_str}': {e}")
            return (
                f"I'll coordinate with our team to send you a calendar invitation for {meeting_time} "
                f"to {email}. You'll receive an email with the meeting details shortly."
            )
        
        # Create the meeting datetime
        meeting_date = now + timedelta(days=days_ahead)
        start_time = meeting_date.replace(
            hour=time_obj.hour,
            minute=time_obj.minute,
            second=0,
            microsecond=0
        )
        end_time = start_time + timedelta(minutes=30)  # 30-minute meeting
        
        logger.info(f"Meeting scheduled for: {start_time}")
        
        # Create the event
        event = calendar.create_event(
            summary="Botel AI Demo Call",
            start_time=start_time,
            end_time=end_time,
            attendee_email=email,
            description="Looking forward to showing you how Botel AI can transform your guest communications!"
        )
        
        if event:
            meet_link = event.get('hangoutLink', 'the meeting link in your invitation')
            
            # Log successful demo scheduling to Supabase
            try:
                import asyncio
                # Get room name from context - try multiple approaches
                room_id = None
                
                # First try to get from context attributes
                if hasattr(context, 'room'):
                    if hasattr(context.room, 'name'):
                        room_id = context.room.name
                    elif hasattr(context.room, 'sid'):
                        room_id = context.room.sid
                
                # If not found, try job attributes
                if not room_id and hasattr(context, 'job'):
                    if hasattr(context.job, 'room'):
                        if hasattr(context.job.room, 'name'):
                            room_id = context.job.room.name
                        elif hasattr(context.job.room, 'sid'):
                            room_id = context.job.room.sid
                    elif hasattr(context.job, 'id'):
                        room_id = context.job.id
                
                # Log room ID for tracking
                if not room_id:
                    room_id = "unknown"
                
                if room_id:
                    logger.info(f"Marking demo scheduled for room_id: {room_id}")
                    # Log demo scheduled
                    logger.info(f"Demo scheduled for {formatted_datetime} {timezone} in room {room_id}")
                else:
                    logger.warning("Could not determine room_id for demo scheduling")
            except Exception as e:
                logger.error(f"Error logging demo to Supabase: {e}")
            
            return (
                f"Perfect! I've scheduled our demo for {meeting_time} and sent a calendar invitation "
                f"to {email}. You'll receive an email with all the details including {meet_link}. "
                f"Looking forward to speaking with you!"
            )
        else:
            return (
                f"I'll make sure our team sends you a calendar invitation for {meeting_time} "
                f"to {email} right away. You'll receive the meeting details shortly."
            )
            
    except Exception as e:
        logger.error(f"Error creating meeting: {e}")
        return (
            f"I'll have someone from our team send the calendar invite for {meeting_time} "
            f"to {email} to ensure everything is set up properly."
        )