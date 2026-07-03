'use client'
import { useState } from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { useTheme } from '@/components/providers'
import {
  LayoutDashboard, Users, Brain, Shield, Database,
  Activity, Settings, AlertTriangle, Server, BarChart2,
  FileText, ChevronLeft, ChevronRight, X, Menu,
  Sun, Moon, TrendingUp, ArrowLeft
} from 'lucide-react'

const ADMIN_NAV = [
  { href: '/admin',              icon: LayoutDashboard, label: 'Overview' },
  { href: '/admin/predictions',  icon: Brain,           label: 'Predictions' },
  { href: '/admin/agents',       icon: Users,           label: 'Agents' },
  { href: '/admin/models',       icon: BarChart2,       label: 'Models' },
  { href: '/admin/alerts',       icon: AlertTriangle,   label: 'Alerts' },
  { href: '/admin/users',        icon: Shield,          label: 'Users' },
  { href: '/admin/data-sources', icon: Database,        label: 'Data Sources' },
  { href: '/admin/data-quality', icon: Activity,        label: 'Data Quality' },
  { href: '/admin/api-health',   icon: Server,          label: 'API Health' },
  { href: '/admin/logs',         icon: FileText,        label: 'Logs' },
  { href: '/admin/system',       icon: Settings,        label: 'System' },
  { href: '/admin/config',       icon: Settings,        label: 'Config' },
]

export default function AdminLayout({ children }) {
  const pathname = usePathname()
  const { theme, toggleTheme } = useTheme()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg-primary)' }}>

      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)} />
      )}

      {/* Admin Sidebar */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-50 flex flex-col
          transition-all duration-300
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          ${collapsed ? 'w-[64px]' : 'w-[232px]'}
          border-r
        `}
        style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
      >
        {/* Brand */}
        <div className="flex items-center justify-between px-4 border-b flex-shrink-0"
          style={{ borderColor: 'var(--border)', height: '64px' }}>
          {!collapsed && (
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="flex items-center justify-center rounded-xl flex-shrink-0"
                style={{ width: 32, height: 32, background: 'linear-gradient(135deg, #B5451B, #D4622E)' }}>
                <Shield size={15} color="#fff" />
              </div>
              <div style={{ fontFamily: "'DM Sans', sans-serif", fontWeight: 800, fontSize: '15px', whiteSpace: 'nowrap' }}>
                <span style={{ color: '#B5451B' }}>Admin</span>
                <span style={{ color: 'var(--text-muted)', fontWeight: 400, fontSize: '13px', marginLeft: '4px' }}>Panel</span>
              </div>
            </div>
          )}
          {collapsed && (
            <div className="flex items-center justify-center w-full">
              <div className="flex items-center justify-center rounded-xl"
                style={{ width: 32, height: 32, background: 'linear-gradient(135deg, #B5451B, #D4622E)' }}>
                <Shield size={15} color="#fff" />
              </div>
            </div>
          )}
          <button onClick={() => setCollapsed(c => !c)}
            className="hidden lg:flex items-center justify-center w-7 h-7 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex-shrink-0 ml-1"
            style={{ color: 'var(--text-muted)' }}>
            {collapsed ? <ChevronRight size={15} /> : <ChevronLeft size={15} />}
          </button>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden p-1" style={{ color: 'var(--text-secondary)' }}>
            <X size={18} />
          </button>
        </div>

        {/* Back to app */}
        {!collapsed && (
          <div className="px-3 pt-3">
            <Link href="/dashboard"
              className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-all hover:bg-gray-100 dark:hover:bg-gray-800"
              style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
              <ArrowLeft size={14} />
              <span>Back to App</span>
            </Link>
          </div>
        )}

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-3 px-2">
          {ADMIN_NAV.map(({ href, icon: Icon, label }) => {
            const active = pathname === href || (href !== '/admin' && pathname.startsWith(href))
            return (
              <Link key={href} href={href} onClick={() => setSidebarOpen(false)}
                title={collapsed ? label : undefined}
                className={`flex items-center gap-3 rounded-xl mb-0.5 font-medium transition-all duration-150
                  ${active ? 'text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-800'}
                  ${collapsed ? 'justify-center px-0 py-3' : 'px-3 py-2.5'}
                `}
                style={{
                  background: active ? '#B5451B' : 'transparent',
                  color: active ? '#fff' : 'var(--text-secondary)',
                  fontSize: '14.5px',
                }}>
                <Icon size={17} style={{ flexShrink: 0 }} />
                {!collapsed && <span>{label}</span>}
              </Link>
            )
          })}
        </nav>

        <div className="border-t p-3 flex-shrink-0" style={{ borderColor: 'var(--border)' }}>
          <button onClick={toggleTheme}
            className={`w-full flex items-center gap-2.5 rounded-xl font-medium transition-all
              hover:bg-gray-100 dark:hover:bg-gray-800
              ${collapsed ? 'justify-center px-0 py-3' : 'px-3 py-2.5'}
            `}
            style={{ color: 'var(--text-secondary)', fontSize: '14.5px' }}>
            {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
            {!collapsed && <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>}
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="lg:hidden flex items-center justify-between px-4 h-14 border-b flex-shrink-0"
          style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
          <button onClick={() => setSidebarOpen(true)} style={{ color: 'var(--text-primary)' }}>
            <Menu size={22} />
          </button>
          <span style={{ fontWeight: 700, fontSize: '16px', color: '#B5451B' }}>Admin Panel</span>
          <button onClick={toggleTheme} style={{ color: 'var(--text-secondary)' }}>
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </header>
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
