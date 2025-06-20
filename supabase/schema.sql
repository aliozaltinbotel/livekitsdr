-- Create conversations table for storing chat history
CREATE TABLE IF NOT EXISTS conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    room_id VARCHAR(255) NOT NULL,
    participant_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'agent')),
    message TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX idx_conversations_room_id ON conversations(room_id);
CREATE INDEX idx_conversations_participant_id ON conversations(participant_id);
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp DESC);

-- Create call_sessions table for tracking calls
CREATE TABLE IF NOT EXISTS call_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    room_id VARCHAR(255) NOT NULL UNIQUE,
    participant_id VARCHAR(255) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'failed')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for call sessions
CREATE INDEX idx_call_sessions_room_id ON call_sessions(room_id);
CREATE INDEX idx_call_sessions_status ON call_sessions(status);

-- Create a view for call summaries
CREATE OR REPLACE VIEW call_summaries AS
SELECT 
    cs.id,
    cs.room_id,
    cs.participant_id,
    cs.started_at,
    cs.ended_at,
    cs.duration_seconds,
    cs.status,
    COUNT(c.id) as message_count,
    COUNT(CASE WHEN c.role = 'user' THEN 1 END) as user_message_count,
    COUNT(CASE WHEN c.role = 'agent' THEN 1 END) as agent_message_count
FROM call_sessions cs
LEFT JOIN conversations c ON cs.room_id = c.room_id
GROUP BY cs.id;

-- Enable Row Level Security
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_sessions ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your auth setup)
CREATE POLICY "Allow authenticated read access" ON conversations
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow service role full access" ON conversations
    FOR ALL
    TO service_role
    USING (true);