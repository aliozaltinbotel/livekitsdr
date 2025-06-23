-- Check the latest test session
-- voice_assistant_room_2671

-- 1. Check session details
SELECT 
    session_id,
    user_name,
    user_email,
    user_phone,
    demo_scheduled,
    demo_time,
    demo_timezone,
    status,
    created_at,
    updated_at
FROM sessions
WHERE session_id = 'voice_assistant_room_2671';

-- 2. Check conversations for this session
SELECT 
    role,
    LEFT(message, 100) as message_preview,
    timestamp
FROM conversations
WHERE session_id = 'voice_assistant_room_2671'
ORDER BY timestamp;

-- 3. Count messages by role
SELECT 
    role,
    COUNT(*) as message_count
FROM conversations
WHERE session_id = 'voice_assistant_room_2671'
GROUP BY role;

-- 4. Check if name "Ali" was captured anywhere
SELECT 
    role,
    message,
    timestamp
FROM conversations
WHERE session_id = 'voice_assistant_room_2671'
AND LOWER(message) LIKE '%ali%'
ORDER BY timestamp;