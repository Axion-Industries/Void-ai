
-- Set JWT secret (replace with your actual secret in production)
-- ALTER DATABASE postgres SET "app.jwt_secret" TO 'your-jwt-secret';


-- Create chats table
CREATE TABLE IF NOT EXISTS public.chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()),
    message TEXT NOT NULL,
    response TEXT,
    embedding float8[]
);


-- Create training_sessions table
CREATE TABLE IF NOT EXISTS public.training_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'training', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);


CREATE INDEX IF NOT EXISTS idx_chats_user_id ON public.chats (user_id);
CREATE INDEX IF NOT EXISTS idx_chats_created_at ON public.chats (created_at);
CREATE INDEX IF NOT EXISTS idx_training_sessions_user_id ON public.training_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_training_sessions_status ON public.training_sessions (status);


ALTER TABLE public.chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.training_sessions ENABLE ROW LEVEL SECURITY;


-- RLS policies for chats
CREATE POLICY "Users can view own chats" ON public.chats FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own chats" ON public.chats FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own chats" ON public.chats FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own chats" ON public.chats FOR DELETE USING (auth.uid() = user_id);

-- RLS policies for training_sessions
CREATE POLICY "Users can view own training_sessions" ON public.training_sessions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own training_sessions" ON public.training_sessions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own training_sessions" ON public.training_sessions FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own training_sessions" ON public.training_sessions FOR DELETE USING (auth.uid() = user_id);


-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for training_sessions
DROP TRIGGER IF EXISTS update_training_sessions_updated_at ON public.training_sessions;
CREATE TRIGGER update_training_sessions_updated_at
    BEFORE UPDATE ON public.training_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();




-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Function for vector similarity search on chats
CREATE OR REPLACE FUNCTION public.match_relevant_chats(
    query_embedding float8[],
    match_threshold float8,
    match_count integer,
    request_user_id uuid
)
RETURNS TABLE(
    id uuid,
    user_id uuid,
    message text,
    response text,
    embedding float8[],
    similarity float8
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.user_id,
        c.message,
        c.response,
        c.embedding,
        (1 - (c.embedding <=> query_embedding)) AS similarity
    FROM public.chats c
    WHERE c.user_id = request_user_id
      AND c.embedding IS NOT NULL
      AND (1 - (c.embedding <=> query_embedding)) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
