-- Supabase Schema for LiveKit Agent Sessions and Conversations

-- Sessions table to track each voice session
CREATE TABLE IF NOT EXISTS sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id TEXT NOT NULL UNIQUE, -- LiveKit room name
    job_id TEXT NOT NULL,
    participant_id TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    status TEXT DEFAULT 'active', -- active, completed, error
    
    -- Collected user data
    user_name TEXT,
    user_email TEXT,
    user_phone TEXT,
    
    -- Demo scheduling
    demo_scheduled BOOLEAN DEFAULT FALSE,
    demo_time TIMESTAMP WITH TIME ZONE,
    demo_timezone TEXT,
    
    -- Metadata
    agent_version TEXT DEFAULT 'jamie-v1',
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations table for detailed message history
CREATE TABLE IF NOT EXISTS conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    room_id TEXT NOT NULL,
    participant_id TEXT,
    role TEXT NOT NULL CHECK (role IN ('agent', 'user', 'system')),
    message TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Additional conversation metadata
    confidence FLOAT, -- STT confidence score
    duration_ms INTEGER, -- How long the utterance took
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tool calls table to track calendar operations
CREATE TABLE IF NOT EXISTS tool_calls (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    tool_name TEXT NOT NULL,
    parameters JSONB,
    result TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_sessions_participant_id ON sessions(participant_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_demo_scheduled ON sessions(demo_scheduled);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp);
CREATE INDEX idx_tool_calls_session_id ON tool_calls(session_id);

-- Create a view for session summaries
CREATE OR REPLACE VIEW session_summaries AS
SELECT 
    s.id,
    s.session_id,
    s.participant_id,
    s.started_at,
    s.ended_at,
    s.duration_seconds,
    s.status,
    s.user_name,
    s.user_email,
    s.user_phone,
    s.demo_scheduled,
    s.demo_time,
    COUNT(DISTINCT c.id) as message_count,
    COUNT(DISTINCT CASE WHEN c.role = 'user' THEN c.id END) as user_message_count,
    COUNT(DISTINCT CASE WHEN c.role = 'agent' THEN c.id END) as agent_message_count
FROM sessions s
LEFT JOIN conversations c ON s.session_id = c.session_id
GROUP BY s.id;

-- Function to update session end time and duration
CREATE OR REPLACE FUNCTION update_session_end_time()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ended_at IS NOT NULL AND OLD.ended_at IS NULL THEN
        NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.ended_at - NEW.started_at))::INTEGER;
    END IF;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update duration when session ends
CREATE TRIGGER update_session_duration
BEFORE UPDATE ON sessions
FOR EACH ROW
EXECUTE FUNCTION update_session_end_time();

-- RLS Policies (if using Row Level Security)
-- ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE tool_calls ENABLE ROW LEVEL SECURITY;