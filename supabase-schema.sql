-- Enable Row Level Security
ALTER DATABASE postgres SET "app.jwt_secret" TO 'your-jwt-secret';

-- Create tables
CREATE TABLE IF NOT EXISTS public.chats (
    id UUID DEFAULT gen_random_uuid () PRIMARY KEY,
    user_id UUID REFERENCES auth.users (id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.training_sessions (
    id UUID DEFAULT gen_random_uuid () PRIMARY KEY,
    user_id UUID REFERENCES auth.users (id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (
        status IN (
            'pending',
            'training',
            'completed',
            'failed'
        )
    ),
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON public.chats (user_id);

CREATE INDEX IF NOT EXISTS idx_chats_created_at ON public.chats (created_at);

CREATE INDEX IF NOT EXISTS idx_training_sessions_user_id ON public.training_sessions (user_id);

CREATE INDEX IF NOT EXISTS idx_training_sessions_status ON public.training_sessions (status);

-- Enable Row Level Security
ALTER TABLE public.chats ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.training_sessions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only see their own chats
CREATE POLICY "Users can view own chats" ON public.chats FOR
SELECT USING (auth.uid () = user_id);

-- Users can only insert their own chats
CREATE POLICY "Users can insert own chats" ON public.chats FOR
INSERT
WITH
    CHECK (auth.uid () = user_id);

-- Users can only update their own chats
CREATE POLICY "Users can update own chats" ON public.chats FOR
UPDATE USING (auth.uid () = user_id);

-- Users can only delete their own chats
CREATE POLICY "Users can delete own chats" ON public.chats FOR DELETE USING (auth.uid () = user_id);

-- Users can only see their own training sessions
CREATE POLICY "Users can view own training sessions" ON public.training_sessions FOR
SELECT USING (auth.uid () = user_id);

-- Users can only insert their own training sessions
CREATE POLICY "Users can insert own training sessions" ON public.training_sessions FOR
INSERT
WITH
    CHECK (auth.uid () = user_id);

-- Users can only update their own training sessions
CREATE POLICY "Users can update own training sessions" ON public.training_sessions FOR
UPDATE USING (auth.uid () = user_id);

-- Users can only delete their own training sessions
CREATE POLICY "Users can delete own training sessions" ON public.training_sessions FOR DELETE USING (auth.uid () = user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for training_sessions
CREATE TRIGGER update_training_sessions_updated_at
    BEFORE UPDATE ON public.training_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
