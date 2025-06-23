-- Check Supabase Data Recording Status
-- Run this in your Supabase SQL editor

-- 1. Check latest sessions with all columns
SELECT 
    session_id,
    job_id,
    participant_id,
    status,
    user_name,
    user_email,
    user_phone,
    demo_scheduled,
    demo_time,
    demo_timezone,
    started_at,
    ended_at,
    duration_seconds,
    created_at,
    updated_at
FROM sessions
ORDER BY created_at DESC
LIMIT 5;

-- 2. Check sessions with any user data
SELECT 
    session_id,
    user_name,
    user_email,
    user_phone,
    demo_scheduled,
    status
FROM sessions
WHERE user_name IS NOT NULL 
   OR user_email IS NOT NULL 
   OR user_phone IS NOT NULL
ORDER BY created_at DESC;

-- 3. Check conversation messages count by session
SELECT 
    s.session_id,
    s.status,
    s.demo_scheduled,
    s.created_at,
    COUNT(CASE WHEN c.role = 'agent' THEN 1 END) as agent_messages,
    COUNT(CASE WHEN c.role = 'user' THEN 1 END) as user_messages,
    COUNT(CASE WHEN c.role = 'system' THEN 1 END) as system_messages,
    COUNT(c.id) as total_messages
FROM sessions s
LEFT JOIN conversations c ON s.session_id = c.session_id
GROUP BY s.session_id, s.status, s.demo_scheduled, s.created_at
ORDER BY s.created_at DESC
LIMIT 10;

-- 4. Check actual conversation content for latest session
SELECT 
    role,
    message,
    participant_id,
    timestamp
FROM conversations
WHERE session_id = (
    SELECT session_id 
    FROM sessions 
    ORDER BY created_at DESC 
    LIMIT 1
)
ORDER BY timestamp;

-- 5. Check tool calls
SELECT 
    session_id,
    tool_name,
    parameters,
    result,
    success,
    timestamp
FROM tool_calls
ORDER BY timestamp DESC
LIMIT 10;

-- 6. Check for sessions that were updated after creation
SELECT 
    session_id,
    created_at,
    updated_at,
    CASE 
        WHEN updated_at > created_at THEN 'Updated'
        ELSE 'Not Updated'
    END as update_status,
    demo_scheduled,
    user_email
FROM sessions
WHERE created_at >= NOW() - INTERVAL '1 day'
ORDER BY created_at DESC;

-- 7. Summary statistics
SELECT 
    COUNT(*) as total_sessions,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_sessions,
    COUNT(CASE WHEN demo_scheduled = true THEN 1 END) as demos_scheduled,
    COUNT(CASE WHEN user_email IS NOT NULL THEN 1 END) as sessions_with_email,
    COUNT(CASE WHEN user_phone IS NOT NULL THEN 1 END) as sessions_with_phone,
    COUNT(CASE WHEN user_name IS NOT NULL THEN 1 END) as sessions_with_name
FROM sessions
WHERE created_at >= NOW() - INTERVAL '7 days';