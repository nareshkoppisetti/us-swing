import AdminLayout from '@/components/layout/AdminLayout'

/**
 * Shared layout for all /admin/* pages.
 *
 * Next.js App Router automatically wraps every page under /admin/ with this
 * layout. This means individual admin pages (system, agents, users, etc.)
 * do NOT need to import or render <AdminLayout> themselves — they just export
 * their page content and this layout provides the shell.
 *
 * Route protection is handled by frontend/src/middleware.js which blocks
 * unauthenticated users and non-admin roles BEFORE this layout even renders.
 *
 * Note: This is a Server Component (no 'use client') intentionally —
 * AdminLayout itself is a Client Component and handles interactivity.
 */
export const metadata = {
  title: 'Admin — USA Swing',
  description: 'USA Swing administration panel',
}

export default function AdminRootLayout({ children }) {
  return <AdminLayout>{children}</AdminLayout>
}
