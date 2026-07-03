'use client'
import { useRouter } from 'next/navigation'
import { ShieldOff, ArrowLeft, Home } from 'lucide-react'

/**
 * 403 — Access Denied
 * Shown by the middleware when an authenticated non-admin ("user" role)
 * attempts to navigate to an admin-only route (/admin/* or /agents/*).
 */
export default function ForbiddenPage() {
  const router = useRouter()

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{ background: 'var(--bg-primary)' }}
    >
      <div className="w-full max-w-md text-center animate-fade-in">
        {/* Icon */}
        <div
          className="mx-auto mb-6 flex items-center justify-center rounded-2xl"
          style={{
            width: 72,
            height: 72,
            background: 'rgba(198,40,40,0.12)',
          }}
        >
          <ShieldOff size={36} color="#B5451B" />
        </div>

        {/* Heading */}
        <h1
          className="text-3xl font-bold mb-2"
          style={{ color: 'var(--text-primary)' }}
        >
          Access Denied
        </h1>
        <p className="text-sm mb-1" style={{ color: 'var(--text-muted)' }}>
          Error 403 — Forbidden
        </p>

        {/* Explanation */}
        <div
          className="card p-5 my-6 text-left text-sm space-y-2"
          style={{ color: 'var(--text-secondary)' }}
        >
          <p>
            The Admin Panel is restricted to{' '}
            <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
              Super Admin
            </span>{' '}
            and{' '}
            <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
              Admin
            </span>{' '}
            roles only.
          </p>
          <p>
            Your current account does not have the required permissions. If you
            believe this is an error, contact your system administrator to
            update your role assignment.
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3 justify-center">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all hover:opacity-80"
            style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border)',
              color: 'var(--text-primary)',
            }}
          >
            <ArrowLeft size={15} />
            Go Back
          </button>
          <button
            onClick={() => router.push('/dashboard')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold text-white transition-all hover:opacity-90"
            style={{ background: 'linear-gradient(135deg, #2A7A6F, #3A9E8F)' }}
          >
            <Home size={15} />
            Dashboard
          </button>
        </div>
      </div>
    </div>
  )
}
