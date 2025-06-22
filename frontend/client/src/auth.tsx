import { AuthError } from '@supabase/supabase-js'
import React, { useState } from 'react'
import { supabase } from './supabase'

interface AuthProps {
  onAuthSuccess: () => void
}

export const Auth: React.FC<AuthProps> = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<AuthError | null>(null)

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      if (isLogin) {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        })
        if (error) throw error
      } else {
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: {
              username: username,
            }
          }
        })
        if (error) throw error
      }
      onAuthSuccess()
    } catch (error: any) {
      setError(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      maxWidth: 400,
      margin: '4rem auto',
      background: '#fff',
      borderRadius: 8,
      boxShadow: '0 2px 8px #0001',
      padding: 24
    }}>
      <h2 style={{ textAlign: 'center', marginBottom: 24, color: '#333' }}>
        {isLogin ? 'Sign In' : 'Create Account'}
      </h2>

      {error && (
        <div style={{
          background: '#fee',
          color: '#c33',
          padding: 12,
          borderRadius: 4,
          marginBottom: 16
        }}>
          {error.message}
        </div>
      )}

      <form onSubmit={handleAuth}>
        {!isLogin && (
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, color: '#333' }}>
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
              style={{
                width: '100%',
                padding: 8,
                borderRadius: 4,
                border: '1px solid #ccc',
                fontSize: 14
              }}
            />
          </div>
        )}

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 4, color: '#333' }}>
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{
              width: '100%',
              padding: 8,
              borderRadius: 4,
              border: '1px solid #ccc',
              fontSize: 14
            }}
          />
        </div>

        <div style={{ marginBottom: 24 }}>
          <label style={{ display: 'block', marginBottom: 4, color: '#333' }}>
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            style={{
              width: '100%',
              padding: 8,
              borderRadius: 4,
              border: '1px solid #ccc',
              fontSize: 14
            }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: 12,
            borderRadius: 4,
            background: '#4b0082',
            color: '#fff',
            border: 0,
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: 14
          }}
        >
          {loading ? 'Loading...' : (isLogin ? 'Sign In' : 'Sign Up')}
        </button>
      </form>

      <div style={{ textAlign: 'center', marginTop: 16 }}>
        <button
          onClick={() => {
            setIsLogin(!isLogin);
            setError(null);
          }}
          style={{
            background: 'none',
            border: 'none',
            color: '#4b0082',
            cursor: 'pointer',
            textDecoration: 'underline',
            fontSize: 14
          }}
        >
          {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
        </button>
      </div>
    </div>
  )
}
