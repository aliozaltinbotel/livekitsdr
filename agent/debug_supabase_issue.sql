-- Debug Supabase Data Recording Issues
-- Run these queries to understand what's happening

-- 1. Check if sessions are being created
SELECT 
    session_id,
    job_id,
    participant_id,
    status,
    created_at,
    updated_at,
    EXTRACT(EPOCH FROM (updated_at - created_at)) as seconds_between_create_update
FROM sessions
ORDER BY created_at DESC
LIMIT 10;

-- 2. Check if conversations are being logged
SELECT 
    c.session_id,
    c.role,
    c.participant_id,
    LEFT(c.message, 50) as message_preview,
    c.timestamp,
    s.status as session_status
FROM conversations c
LEFT JOIN sessions s ON c.session_id = s.session_id
ORDER BY c.timestamp DESC
LIMIT 20;

-- 3. Check for sessions that have conversations but no user data
SELECT 
    s.session_id,
    s.user_name,
    s.user_email,
    s.user_phone,
    s.demo_scheduled,
    s.created_at,
    COUNT(c.id) as conversation_count,
    COUNT(CASE WHEN c.role = 'user' THEN 1 END) as user_messages,
    COUNT(CASE WHEN c.role = 'agent' THEN 1 END) as agent_messages
FROM sessions s
LEFT JOIN conversations c ON s.session_id = c.session_id
GROUP BY s.session_id, s.user_name, s.user_email, s.user_phone, s.demo_scheduled, s.created_at
HAVING COUNT(c.id) > 0
ORDER BY s.created_at DESC;

-- 4. Check if updates are being applied
SELECT 
    session_id,
    created_at,
    updated_at,
    user_name,
    user_email,
    user_phone,
    demo_scheduled,
    demo_time,
    CASE 
        WHEN updated_at = created_at THEN 'Never Updated'
        WHEN updated_at > created_at THEN 'Updated'
    END as update_status
FROM sessions
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- 5. Look for any pattern in message logging
WITH message_timing AS (
    SELECT 
        session_id,
        role,
        timestamp,
        LAG(timestamp) OVER (PARTITION BY session_id ORDER BY timestamp) as prev_timestamp,
        EXTRACT(EPOCH FROM (timestamp - LAG(timestamp) OVER (PARTITION BY session_id ORDER BY timestamp))) as seconds_since_last
    FROM conversations
)
SELECT 
    session_id,
    COUNT(*) as message_count,
    COUNT(CASE WHEN role = 'system' THEN 1 END) as system_msgs,
    COUNT(CASE WHEN role = 'user' THEN 1 END) as user_msgs,
    COUNT(CASE WHEN role = 'agent' THEN 1 END) as agent_msgs,
    AVG(seconds_since_last) FILTER (WHERE seconds_since_last IS NOT NULL) as avg_seconds_between_msgs
FROM message_timing
GROUP BY session_id
ORDER BY MIN(timestamp) DESC;

-- 6. Check the exact session that was mentioned in logs
SELECT 
    s.*,
    (SELECT COUNT(*) FROM conversations c WHERE c.session_id = s.session_id) as total_messages,
    (SELECT COUNT(*) FROM conversations c WHERE c.session_id = s.session_id AND c.role = 'user') as user_messages,
    (SELECT COUNT(*) FROM conversations c WHERE c.session_id = s.session_id AND c.role = 'agent') as agent_messages,
    (SELECT COUNT(*) FROM tool_calls t WHERE t.session_id = s.session_id) as tool_calls
FROM sessions s
WHERE s.session_id = 'voice_assistant_room_5464';