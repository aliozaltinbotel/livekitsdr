# Google Calendar API Setup Guide

This guide will help you set up Google Calendar API integration for your LiveKit voice agent.

## Overview

The Google Calendar integration allows your voice agent to:
- Check real calendar availability
- Create calendar events directly
- Send email invitations automatically
- Include Google Meet links in appointments

## Prerequisites

1. A Google account with Google Calendar
2. Access to Google Cloud Console
3. Python dependencies installed (`pip install -r requirements.txt`)

## Setup Instructions

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., "Botel AI Calendar")
4. Click "Create"

### Step 2: Enable Google Calendar API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

### Step 3: Create Credentials

You have two options:

#### Option A: OAuth 2.0 (Recommended for User Calendars)

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: Internal (for testing) or External
   - Fill in required fields
   - Add scope: `https://www.googleapis.com/auth/calendar`
4. Application type: Desktop app
5. Name: "LiveKit Agent"
6. Click "Create"
7. Download the JSON file and save it as `credentials.json`

#### Option B: Service Account (For Dedicated Calendar)

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service account"
3. Fill in service account details
4. Click "Create and Continue"
5. Grant role: "Calendar Admin" or "Calendar Editor"
6. Click "Done"
7. Click on the service account → "Keys" → "Add Key" → "Create new key"
8. Choose JSON format
9. Save the downloaded file as `service-account-key.json`

### Step 4: Configure Environment Variables

Add to your `.env` file:

```bash
# For OAuth2 (Option A)
GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json

# For Service Account (Option B)
GOOGLE_SERVICE_ACCOUNT_KEY=/path/to/service-account-key.json

# Calendar ID (use "primary" for main calendar)
GOOGLE_CALENDAR_ID=primary
```

### Step 5: First-Time Authentication (OAuth2 Only)

If using OAuth2, you'll need to authenticate once:

1. Create a simple authentication script:

```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate():
    creds = None
    token_path = 'token.json'
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv('GOOGLE_CREDENTIALS_PATH'), SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    print("Authentication successful!")

if __name__ == '__main__':
    authenticate()
```

2. Run the script: `python authenticate.py`
3. Follow the browser prompts to authorize
4. A `token.json` file will be created

### Step 6: Update google_calendar_tools.py

Update the `_initialize_service` method to use the token:

```python
def _initialize_service(self):
    """Initialize Google Calendar service with credentials"""
    try:
        creds = None
        token_path = 'token.json'
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path)
            
        if creds and creds.valid:
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Google Calendar service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Google Calendar: {e}")
```

## Testing the Integration

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start your agent:
   ```bash
   python agent.py dev
   ```

3. Test the calendar tools:
   - When asked about scheduling, the agent will check real availability
   - When confirming a time, it will create an actual calendar event
   - The attendee will receive an email invitation with Google Meet link

## Troubleshooting

### "Credentials not found" Error
- Ensure your credentials file path is correct in `.env`
- Check file permissions

### "Calendar API not enabled" Error
- Go back to Google Cloud Console
- Ensure Calendar API is enabled for your project

### "Insufficient permissions" Error
- Check the OAuth scopes include calendar access
- For service accounts, ensure it has Calendar Editor role

### No Available Slots Shown
- Check your calendar isn't fully booked
- Verify timezone settings are correct
- Ensure business hours logic matches your availability

## Security Notes

1. **Never commit credentials to git**
   - Add `*.json` to `.gitignore`
   - Keep credentials files secure

2. **Use environment variables**
   - Store paths in `.env` file
   - Don't hardcode credentials

3. **Limit scope access**
   - Only request calendar permissions needed
   - Use read-only access where possible

## Next Steps

1. Customize the event creation logic in `google_calendar_create_meeting()`
2. Add support for different meeting durations
3. Implement recurring event support
4. Add calendar conflict detection
5. Create custom email templates for invitations