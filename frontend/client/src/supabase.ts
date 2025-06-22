/// <reference types="vite/client" />

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables. Make sure to create a .env file in the /frontend directory.')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types
export interface User {
  id: string
  email: string
  created_at: string
  updated_at: string
}

export interface Chat {
  id: string
  user_id: string
  message: string
  response: string
  created_at: string
}

export interface TrainingSession {
  id: string
  user_id: string
  text: string
  status: 'pending' | 'training' | 'completed' | 'failed'
  created_at: string
  updated_at: string
}

export interface Profile {
  id: string
  updated_at: string
  username: string
  full_name: string
  avatar_url: string
  website: string
}
