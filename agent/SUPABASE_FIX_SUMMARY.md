# Supabase Data Recording Issues - Analysis and Fixes

## Issues Identified

### 1. Room ID Mismatch in Calendar Tool
- **Problem**: When scheduling a demo, the `google_calendar_tools.py` was defaulting to room_id="unknown"
- **Impact**: Demo scheduling updates were failing because they tried to update a non-existent session
- **Fix**: Enhanced room ID detection logic to try multiple approaches to get the correct room ID

### 2. Missing Event Handler Logs
- **Problem**: Speech events (user/agent) might not be getting logged properly
- **Impact**: No conversation history in Supabase
- **Fix**: Added more detailed logging to track when events are fired and logged

### 3. Session Update Failures
- **Problem**: Updates were failing silently when session didn't exist
- **Impact**: User data (name, email, phone) not being stored
- **Fix**: Added upsert logic to create session if it doesn't exist during updates

## Fixes Applied

### 1. google_calendar_tools.py (lines 407-443)
```python
# Enhanced room ID detection with multiple fallbacks:
- Try context.room.name and context.room.sid
- Try context.job.room.name and context.job.room.sid
- Try context.job.id
- Try supabase_logger.current_session_id
- Log warning if room_id cannot be determined
```

### 2. agent.py (lines 328-398)
```python
# Added detailed logging for debugging:
- Log when speech events are committed
- Log the room_id being used for storage
- Log when user data is extracted
```

### 3. supabase_logger.py (lines 142-172)
```python
# Added fallback creation logic:
- If update fails (no rows updated), attempt to create the session
- Use upsert to handle race conditions
- Better error logging with actual data being sent
```

## Root Causes

1. **Async Context Loss**: The function tools (like calendar) run in a different context where room information isn't directly available
2. **Event Handler Registration**: Need to verify that speech event handlers are properly registered and firing
3. **Session Creation Timing**: Sessions might be created after some events have already occurred

## Testing Steps

1. Deploy the updated code
2. Make a test call and:
   - Provide name, email, phone
   - Schedule a demo
3. Run the debug SQL queries in `debug_supabase_issue.sql`
4. Check logs for:
   - "Session started: [room_id]"
   - "User speech committed: [text]"
   - "Agent speech committed: [text]"
   - "Extracted name/email/phone: [value]"
   - "Session data updated successfully"

## Additional Recommendations

1. **Add Session State Tracking**: Consider adding a session state manager that maintains room context across all components
2. **Implement Event Queue**: Buffer events until session is confirmed created
3. **Add Health Check**: Periodically verify Supabase connection and log any issues
4. **Consider Retry Logic**: Add exponential backoff for failed Supabase operations

## Monitoring

After deployment, monitor these log patterns:
```bash
# Check for successful updates
az container logs --resource-group livekitsdr-rg --name livekitsdr-agent-container | grep "Session data updated successfully"

# Check for extraction
az container logs --resource-group livekitsdr-rg --name livekitsdr-agent-container | grep "Extracted"

# Check for room ID issues
az container logs --resource-group livekitsdr-rg --name livekitsdr-agent-container | grep -E "room_id|unknown"
```