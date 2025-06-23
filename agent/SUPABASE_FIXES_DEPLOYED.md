# Supabase Integration Fixes - Ready for Deployment

## Key Changes Made to agent.py

### 1. Event Handler Updates
- **Problem**: The expected events `agent_speech_committed` and `user_speech_committed` are not available in the current LiveKit setup
- **Solution**: 
  - Using `user_input_transcribed` event to capture user speech
  - Added fallback monitoring of conversation history to capture agent messages
  - Still trying original events in case they become available

### 2. Data Extraction Refactored
- Moved data extraction logic to a helper function `extract_user_data()`
- This function is called from both event handlers to extract:
  - User name (when agent asks for first name)
  - Email address (regex pattern matching)
  - Phone number (flexible pattern matching)

### 3. Conversation History Monitor
- Added `monitor_conversation()` function that runs in background
- Checks session.chat_ctx.messages every second for new messages
- Captures agent messages that might be missed by events

### 4. Enhanced Logging
- Added detailed logging to track:
  - Session type and available events
  - Event registration success/failure
  - Data extraction success
  - Message logging to Supabase

## Other Files Fixed

### google_calendar_tools.py
- Enhanced room ID detection with multiple fallback approaches
- Now checks context.room, context.job, and supabase_logger.current_session_id

### supabase_logger.py
- Added upsert logic when updates fail
- Better error handling and logging

### debug_supabase_issue.sql
- Fixed GROUP BY error in query #3

## Testing After Deployment

1. Deploy the updated code
2. Make a test call and provide:
   - Your name when asked
   - Email address
   - Phone number with country code
   - Schedule a demo

3. Check logs for these key indicators:
```bash
# Check if events are working
az container logs --resource-group livekitsdr-rg --name livekitsdr-agent-container | grep -E "User transcribed|Agent from history|Extracted"

# Check session updates
az container logs --resource-group livekitsdr-rg --name livekitsdr-agent-container | grep "Session data updated"
```

4. Run the SQL queries to verify data is recorded:
```sql
-- Check latest session
SELECT * FROM sessions 
ORDER BY created_at DESC 
LIMIT 1;

-- Check conversations
SELECT * FROM conversations 
WHERE session_id = (SELECT session_id FROM sessions ORDER BY created_at DESC LIMIT 1)
ORDER BY timestamp;
```

## Expected Behavior

- User speech will be captured via `user_input_transcribed` event
- Agent speech will be captured via conversation history monitoring
- User data (name, email, phone) will be extracted and stored
- Demo scheduling will update the session with demo details
- All messages will be logged to the conversations table

## Known Limitations

- Agent messages may have a 1-second delay due to polling interval
- Some agent messages might be missed if they're very short-lived
- The event system seems to be different from the documentation

## Future Improvements

Consider upgrading LiveKit Agents framework or investigating why the standard speech events aren't available.