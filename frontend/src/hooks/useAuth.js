'use client'
import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { getCookie, clearAuthCookies, logout as apiLogout, refreshToken } from '@/lib/api'
import api from '@/lib/api'

/**
 * useAuth — authentication state hook
 *
 * Reads the JWT from the "usa-swing-token" cookie (written by lib/api.js login())
 * and exposes:
 *   - user        : decoded user object (id, username, role, email) | null
 *   - role        : string role | null ("admin" or "user")
 *   - isAdmin     : true if role is "admin"
 *   - authenticated: boolean
 *   - loading     : boolean
 *   - logout()    : function
 *   - refreshUser(): re-fetch /auth/me from the backend
 *
 * The middleware in frontend/src/middleware.js enforces route access.
 * This hook is for UI rendering decisions (show/hide admin links, etc.).
 */

function decodeJwtPayload(token) {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const padded = base64.padEnd(base64.length + (4 - (base64.length % 4)) % 4, '=')
    return JSON.parse(atob(padded))
  } catch {
    return null
  }
}

function isTokenValid(token) {
  const payload = decodeJwtPayload(token)
  if (!payload?.exp) return false
  return payload.exp * 1000 > Date.now()
}

export function useAuth() {
  const router = useRouter()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Fetch full user profile from the backend
  const refreshUser = useCallback(async () => {
    const token = getCookie('usa-swing-token')
    if (!token || !isTokenValid(token)) {
      setUser(null)
      setLoading(false)
      return
    }

    // Seed immediately from cookies set at login — this is what makes the
    // username show up instantly instead of waiting on (or failing back
    // from) a network round-trip. NOTE: the JWT's "sub" claim is the
    // user's UUID, not a display name — it must never be shown in the UI.
    const payload = decodeJwtPayload(token)
    const cachedUsername = getCookie('usa-swing-username')
    const cachedRole = getCookie('usa-swing-role')
    if (cachedUsername) {
      setUser(prev => prev ?? { username: cachedUsername, role: cachedRole || payload?.role })
    }

    try {
      const { data } = await api.get('/api/v1/auth/me')
      const freshUser = data.data ?? data
      setUser(freshUser)
      if (freshUser?.username && typeof document !== 'undefined') {
        const d = new Date()
        d.setTime(d.getTime() + 15 * 60 * 1000)
        document.cookie = `usa-swing-username=${encodeURIComponent(freshUser.username)};expires=${d.toUTCString()};path=/;SameSite=Lax`
      }
    } catch (err) {
      if (err?.message === 'Unauthorized') {
        // Genuinely unauthorized (token + refresh both failed) — clear session
        setUser(null)
        clearAuthCookies()
      } else if (!cachedUsername) {
        // No cached username and the profile fetch failed — nothing real to show.
        setUser({ username: 'User', role: payload?.role })
      }
      // else: keep the cookie-seeded user set above — don't overwrite a real
      // username with a generic placeholder just because /auth/me failed.
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshUser()
  }, [refreshUser])

  // Auto-refresh token 2 minutes before the 15-min expiry
  useEffect(() => {
    const token = getCookie('usa-swing-token')
    if (!token) return
    const payload = decodeJwtPayload(token)
    if (!payload?.exp) return
    const msUntilExpiry = payload.exp * 1000 - Date.now()
    const refreshIn = Math.max(msUntilExpiry - 2 * 60 * 1000, 0)
    const timer = setTimeout(async () => {
      try {
        await refreshToken()
      } catch {
        clearAuthCookies()
        router.push('/login?reason=session_expired')
      }
    }, refreshIn)
    return () => clearTimeout(timer)
  }, [user, router])

  const logout = useCallback(async () => {
    await apiLogout()
    setUser(null)
    router.push('/login')
    router.refresh()
  }, [router])

  const role = user?.role ?? getCookie('usa-swing-role') ?? null

  return {
    user,
    role,
    loading,
    authenticated: !!user,
    isAdmin: role === 'admin',
    logout,
    refreshUser,
  }
}

export default useAuth
