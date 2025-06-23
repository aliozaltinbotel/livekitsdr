# Supabase Integration for LiveKit Agent

This document describes the comprehensive session and conversation logging implementation for the LiveKit voice agent.

## Features

### 1. Session Tracking
- Records every voice session with start/end times
- Tracks session duration and status
- Associates sessions with LiveKit room and participant IDs
- Stores collected user information (name, email, phone)

### 2. Conversation History
- Logs every message from both agent and user
- Timestamps all messages
- Maintains conversation order
- Links messages to their session

### 3. User Data Collection
- Automatically extracts and stores:
  - Email addresses from conversation
  - Phone numbers from conversation
  - User names when provided
- Updates session record with collected data

### 4. Tool Call Logging
- Records all calendar function calls
- Tracks parameters and results
- Logs success/failure status
- Useful for debugging and analytics

### 5. Demo Scheduling Tracking
- Marks when demos are successfully scheduled
- Stores demo time and timezone
- Links to the session for conversion tracking

## Database Schema

Run the SQL in `supabase_schema.sql` to create:

### Tables:
1. **sessions** - Main session tracking
2. **conversations** - Message history
3. **tool_calls** - Function call logs

### Views:
- **session_summaries** - Aggregated session data with message counts

## Environment Variables

Required:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

## Usage

The integration is automatic once environment variables are set:

1. **Session starts** when agent connects
2. **Messages logged** automatically via event handlers
3. **User data extracted** from conversation text
4. **Demo scheduling tracked** when calendar invite sent
5. **Session ends** when participant disconnects

## Data Flow

```
User connects → Session created in Supabase
     ↓
Conversation → Each message logged with timestamp
     ↓
Data extraction → Email/phone detected and stored
     ↓
Tool calls → Calendar operations logged
     ↓
Demo scheduled → Session marked with demo details
     ↓
User disconnects → Session ended with duration
```

## Querying Data

### Recent Sessions
```sql
SELECT * FROM session_summaries 
ORDER BY started_at DESC 
LIMIT 10;
```

### Sessions with Demos Scheduled
```sql
SELECT * FROM sessions 
WHERE demo_scheduled = true 
ORDER BY demo_time;
```

### Full Conversation for a Session
```sql
SELECT * FROM conversations 
WHERE session_id = 'your-session-id' 
ORDER BY timestamp;
```

### Conversion Rate
```sql
SELECT 
  COUNT(*) as total_sessions,
  COUNT(CASE WHEN demo_scheduled THEN 1 END) as demos_scheduled,
  ROUND(COUNT(CASE WHEN demo_scheduled THEN 1 END)::numeric / COUNT(*) * 100, 2) as conversion_rate
FROM sessions
WHERE started_at > NOW() - INTERVAL '7 days';
```

## Privacy Considerations

- All conversations are logged - ensure users are informed
- Sensitive data (emails, phones) are stored - implement appropriate access controls
- Consider data retention policies
- Enable Row Level Security (RLS) in production

## Debugging

Check logs for:
- "Supabase client initialized successfully" - Confirms connection
- "Session started: [room_id]" - New session created
- "Error logging to Supabase" - Connection or permission issues

## Future Enhancements

1. **Analytics Dashboard** - Build visualizations on top of this data
2. **Lead Scoring** - Score leads based on conversation patterns
3. **Follow-up Automation** - Trigger emails based on session outcomes
4. **Sentiment Analysis** - Analyze conversation sentiment
5. **Performance Metrics** - Track agent response times and quality