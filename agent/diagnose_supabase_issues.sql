-- Diagnose Supabase Recording Issues
-- Run this to identify what's not working

-- 1. Find sessions with demo scheduled but missing user data
SELECT 
    session_id,
    demo_scheduled,
    user_email,
    demo_time,
    status,
    created_at,
    updated_at
FROM sessions
WHERE demo_scheduled = true 
  AND (user_email IS NULL OR user_phone IS NULL)
ORDER BY created_at DESC;

-- 2. Check if updates are actually happening
SELECT 
    session_id,
    created_at,
    updated_at,
    created_at = updated_at as never_updated,
    status,
    demo_scheduled
FROM sessions
ORDER BY created_at DESC
LIMIT 10;

-- 3. Check conversation flow for a specific session
-- Replace 'voice_assistant_room_8234' with your session ID
WITH session_timeline AS (
    SELECT 
        'conversation' as event_type,
        c.timestamp,
        c.role || ': ' || LEFT(c.message, 100) as event_description
    FROM conversations c
    WHERE c.session_id = 'voice_assistant_room_8234'
    
    UNION ALL
    
    SELECT 
        'tool_call' as event_type,
        t.timestamp,
        'Tool: ' || t.tool_name || ' - ' || COALESCE(LEFT(t.result, 50), 'No result') as event_description
    FROM tool_calls t
    WHERE t.session_id = 'voice_assistant_room_8234'
    
    UNION ALL
    
    SELECT 
        'session_update' as event_type,
        s.updated_at as timestamp,
        'Session updated - Demo: ' || s.demo_scheduled || ', Email: ' || COALESCE(s.user_email, 'NULL') as event_description
    FROM sessions s
    WHERE s.session_id = 'voice_assistant_room_8234'
)
SELECT * FROM session_timeline
ORDER BY timestamp;

-- 4. Check if there are any orphaned conversations (no matching session)
SELECT 
    c.session_id,
    COUNT(*) as message_count,
    MIN(c.timestamp) as first_message,
    MAX(c.timestamp) as last_message
FROM conversations c
LEFT JOIN sessions s ON c.session_id = s.session_id
WHERE s.id IS NULL
GROUP BY c.session_id;

-- 5. Check for duplicate sessions
SELECT 
    session_id,
    COUNT(*) as duplicate_count
FROM sessions
GROUP BY session_id
HAVING COUNT(*) > 1;

-- 6. Recent session activity with details
SELECT 
    s.session_id,
    s.status,
    s.demo_scheduled,
    s.user_email,
    s.started_at,
    s.ended_at,
    EXTRACT(EPOCH FROM (COALESCE(s.ended_at, NOW()) - s.started_at))/60 as duration_minutes,
    (SELECT COUNT(*) FROM conversations c WHERE c.session_id = s.session_id) as message_count
FROM sessions s
WHERE s.created_at >= NOW() - INTERVAL '1 hour'
ORDER BY s.created_at DESC;