import { NextResponse } from 'next/server'

// ─────────────────────────────────────────────────────────────────────────────
// USA Swing — Route Guard Middleware
//
// Runs on every matched request BEFORE the page renders.
// Responsibilities:
//   1. Redirect unauthenticated users to /login (for any protected route)
//   2. Redirect authenticated non-admin users away from /admin/* with 403 page
//   3. Redirect already-authenticated users away from /login to /dashboard
//
// Token storage (matches lib/api.js):
//   - Access token  → cookie  "usa-swing-token"   (set on login, HttpOnly in prod)
//   - Role claim    → cookie  "usa-swing-role"     (set on login, readable by middleware)
//
// Only two roles exist in this app: "admin" and "user".
//
// Routes that require the admin role (spec Section 8.3):
//   /admin/*   — user management, system config
//   /agents/*  — triggering agent runs (mirrors the backend's require_admin
//                guard on POST /api/v1/agents/run and /run/{agent_id})
//
// Normal "user" accounts are blocked from these and redirected to /403.
// ─────────────────────────────────────────────────────────────────────────────

/** Routes that require authentication but are NOT admin-only */
const PROTECTED_PREFIXES = [
  '/dashboard',
  '/predictions',
  '/news',
  '/signals',
  '/institutional-flows',
  '/options-intelligence',
  '/backtesting',
  '/performance',
  '/history',
  '/alerts',
  '/explanations',
  '/settings',
]

/** Route prefixes that require the admin role */
const ADMIN_PREFIXES = ['/admin', '/agents']

/**
 * Decode a JWT payload WITHOUT verifying the signature.
 * Middleware runs on the Edge runtime which cannot use crypto libraries.
 * Signature verification happens on the FastAPI backend for every API call —
 * this decode is only used to read the role claim for client-side routing.
 * A tampered token will be rejected by the backend on the first API request.
 */
function decodeJwtPayload(token) {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    // Base64url → Base64 → JSON
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const padded = base64.padEnd(base64.length + (4 - (base64.length % 4)) % 4, '=')
    const json = atob(padded)
    return JSON.parse(json)
  } catch {
    return null
  }
}

/**
 * Check whether a JWT token is still valid (not expired).
 */
function isTokenValid(token) {
  const payload = decodeJwtPayload(token)
  if (!payload || !payload.exp) return false
  // exp is Unix seconds; Date.now() is milliseconds
  return payload.exp * 1000 > Date.now()
}

/**
 * Extract role from JWT payload.
 * Falls back to the "usa-swing-role" cookie (set explicitly at login)
 * so the middleware works even if the token payload changes structure.
 */
function getRoleFromRequest(request, token) {
  // Primary: parse from JWT payload
  if (token) {
    const payload = decodeJwtPayload(token)
    if (payload?.role) return payload.role
  }
  // Fallback: explicit role cookie
  return request.cookies.get('usa-swing-role')?.value ?? null
}

export function middleware(request) {
  const { pathname } = request.nextUrl

  const token = request.cookies.get('usa-swing-token')?.value ?? null
  const authenticated = token ? isTokenValid(token) : false
  const role = authenticated ? getRoleFromRequest(request, token) : null

  // ── 1. Already logged in → don't show login page again ──────────────────────
  if (pathname === '/login' || pathname === '/') {
    if (authenticated) {
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }
    return NextResponse.next()
  }

  // ── 2. Admin-only routes — require role === 'admin' ───────────────────────────
  if (ADMIN_PREFIXES.some((prefix) => pathname.startsWith(prefix))) {
    if (!authenticated) {
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      loginUrl.searchParams.set('reason', 'unauthenticated')
      return NextResponse.redirect(loginUrl)
    }
    if (role !== 'admin') {
      // Authenticated but wrong role → 403 page
      return NextResponse.redirect(new URL('/403', request.url))
    }
    return NextResponse.next()
  }

  // ── 3. All other protected routes — require any valid login ──────────────────
  const isProtected = PROTECTED_PREFIXES.some((prefix) =>
    pathname.startsWith(prefix)
  )
  if (isProtected && !authenticated) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('redirect', pathname)
    loginUrl.searchParams.set('reason', 'unauthenticated')
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

// ── Matcher: run middleware on all routes except static assets & API routes ───
export const config = {
  matcher: [
    /*
     * Match every path EXCEPT:
     *   - _next/static  (Next.js build output)
     *   - _next/image   (image optimisation)
     *   - favicon.ico
     *   - Files with an extension (js, css, png, svg, etc.)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|css|js|woff2?)$).*)',
  ],
}