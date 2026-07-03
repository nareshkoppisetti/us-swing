'use client'
import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useTheme } from '@/components/providers'
import { login } from '@/lib/api'
import { TrendingUp, Eye, EyeOff, Sun, Moon, AlertCircle } from 'lucide-react'

// Wrapped in Suspense because useSearchParams needs it in Next.js App Router
function LoginForm() {
  const { theme, toggleTheme } = useTheme()
  const router = useRouter()
  const searchParams = useSearchParams()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Show contextual messages based on redirect reason
  const reason = searchParams.get('reason')
  const redirectTo = searchParams.get('redirect') || '/dashboard'

  useEffect(() => {
    if (reason === 'session_expired') setError('Your session expired. Please sign in again.')
    if (reason === 'unauthenticated') setError('Please sign in to continue.')
  }, [reason])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!username.trim() || !password) {
      setError('Username and password are required.')
      return
    }

    setLoading(true)
    try {
      const { user } = await login(username.trim(), password)
      // Redirect admins to /admin, normal users to /dashboard (or the redirect param)
      const isAdmin = user?.role === 'admin'
      const destination = isAdmin ? '/admin/api-health' : redirectTo
      router.push(destination)
      router.refresh() // re-run middleware with new cookies
    } catch (err) {
      const msg =
        err?.response?.data?.error?.message ||
        err?.response?.data?.detail ||
        'Invalid credentials. Please try again.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{ background: 'var(--bg-primary)' }}
    >
      {/* Theme toggle */}
      <button
        onClick={toggleTheme}
        className="fixed top-4 right-4 p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        style={{ color: 'var(--text-secondary)' }}
        aria-label="Toggle theme"
      >
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </button>

      <div className="w-full max-w-md animate-fade-in">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div
            className="flex items-center justify-center rounded-2xl mb-4"
            style={{
              width: 64,
              height: 64,
              background: 'linear-gradient(135deg, #2A7A6F, #3A9E8F)',
            }}
          >
            <TrendingUp size={32} color="#fff" />
          </div>
          <div style={{ textAlign: 'center' }}>
            <div
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontWeight: 800,
                fontSize: '24px',
                letterSpacing: '-0.02em',
              }}
            >
              <span style={{ color: '#111' }}>USA</span>
              <span
                style={{
                  color: '#111',
                  fontWeight: 400,
                  fontSize: '20px',
                  margin: '0 5px',
                }}
              >
                Swing
              </span>
            </div>
          </div>
        </div>

        {/* Card */}
        <div className="card p-8">
          <h2
            className="text-xl font-bold mb-1"
            style={{ color: 'var(--text-primary)' }}
          >
            Welcome back
          </h2>
          <p className="text-sm mb-6" style={{ color: 'var(--text-muted)' }}>
            Sign in to your account
          </p>

          {/* Error banner */}
          {error && (
            <div
              className="flex items-start gap-2 p-3 rounded-xl mb-4 text-sm"
              style={{
                background: 'rgba(198,40,40,0.1)',
                border: '1px solid rgba(198,40,40,0.3)',
                color: '#B5451B',
              }}
            >
              <AlertCircle size={15} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username */}
            <div>
              <label
                className="block text-sm font-medium mb-1.5"
                style={{ color: 'var(--text-secondary)' }}
              >
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="your_username"
                autoComplete="username"
                className="w-full px-4 py-2.5 rounded-xl text-sm transition-all outline-none"
                style={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border)',
                  color: 'var(--text-primary)',
                  fontFamily: "'DM Sans', sans-serif",
                }}
                disabled={loading}
              />
            </div>

            {/* Password */}
            <div>
              <label
                className="block text-sm font-medium mb-1.5"
                style={{ color: 'var(--text-secondary)' }}
              >
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  autoComplete="current-password"
                  className="w-full px-4 py-2.5 rounded-xl text-sm transition-all outline-none pr-11"
                  style={{
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border)',
                    color: 'var(--text-primary)',
                    fontFamily: "'DM Sans', sans-serif",
                  }}
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                  style={{ color: 'var(--text-muted)' }}
                  tabIndex={-1}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-xl font-semibold text-sm text-white transition-all hover:opacity-90 active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed"
              style={{
                background: 'linear-gradient(135deg, #2A7A6F, #3A9E8F)',
                marginTop: '8px',
              }}
            >
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>
        </div>

        <p className="text-center text-xs mt-4" style={{ color: 'var(--text-muted)' }}>
          Contact your administrator if you need access.
        </p>
      </div>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  )
}
