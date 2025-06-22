# Supabase Setup Guide

This guide will help you set up Supabase for user authentication and data storage for your Void AI Chat & Trainer application.

## 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - Name: `void-ai-chat` (or your preferred name)
   - Database Password: Choose a strong password
   - Region: Choose the closest region to your users
5. Click "Create new project"

## 2. Get Your Project Credentials

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (looks like: `https://your-project-id.supabase.co`)
   - **anon public** key (starts with `eyJ...`)

## 3. Set Up Environment Variables

1. In your `frontend` directory, create a `.env` file:

   ```bash
   cp env.example .env
   ```

2. Edit the `.env` file and replace the placeholder values:
   ```
   VITE_SUPABASE_URL=https://your-project-id.supabase.co
   VITE_SUPABASE_ANON_KEY=your_actual_anon_key_here
   ```

## 4. Set Up Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Copy the contents of `supabase-schema.sql` and paste it into the SQL editor
3. Click "Run" to execute the SQL

This will create:

- `chats` table for storing chat messages
- `training_sessions` table for storing AI training data
- Row Level Security (RLS) policies to ensure users can only access their own data
- Indexes for better performance

## 5. Configure Authentication

1. In your Supabase dashboard, go to **Authentication** → **Settings**
2. Configure your site URL (e.g., `http://localhost:5173` for development)
3. Add any additional redirect URLs if needed

## 6. Install Dependencies

Run the following command in your `frontend` directory:

```bash
npm install
```

## 7. Test the Setup

1. Start your development server:

   ```bash
   npm run dev
   ```

2. Visit your application and try to:
   - Sign up with a new account
   - Sign in with existing credentials
   - Send a chat message (it should be saved to the database)
   - Train the AI (training sessions should be saved)

## 8. Verify Data Storage

1. In your Supabase dashboard, go to **Table Editor**
2. Check the `chats` and `training_sessions` tables
3. You should see your data being stored there

## Security Features

The setup includes:

- **Row Level Security (RLS)**: Users can only access their own data
- **Authentication**: Secure user signup/login
- **Data Validation**: Proper constraints and checks
- **Automatic Timestamps**: Created/updated timestamps are automatically managed

## Troubleshooting

### Common Issues:

1. **"Missing Supabase environment variables"**

   - Make sure your `.env` file exists and has the correct values
   - Restart your development server after changing environment variables

2. **"Invalid API key"**

   - Double-check your anon key in the `.env` file
   - Make sure you're using the "anon public" key, not the service role key

3. **"Table doesn't exist"**

   - Make sure you've run the SQL schema in the Supabase SQL Editor
   - Check that the table names match exactly

4. **Authentication not working**
   - Verify your site URL in Supabase Authentication settings
   - Check that your redirect URLs are configured correctly

## Next Steps

Once the basic setup is working, you can:

1. **Add Social Authentication**: Configure Google, GitHub, etc. in Supabase Auth settings
2. **Add User Profiles**: Create additional user profile fields
3. **Implement Real-time Features**: Use Supabase's real-time subscriptions
4. **Add Admin Features**: Create admin-only views and functionality
5. **Set Up Backups**: Configure automatic database backups

## Production Deployment

For production:

1. Update your site URL in Supabase to your production domain
2. Set up proper CORS settings
3. Configure email templates for authentication
4. Set up monitoring and logging
5. Consider using Supabase's edge functions for server-side logic
