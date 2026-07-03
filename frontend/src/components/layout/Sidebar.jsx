'use client'
import { useState } from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { useTheme } from '@/components/providers'
import { useAuth } from '@/hooks/useAuth'
import {
  LayoutDashboard, Newspaper, Brain, Target, Bell,
  Users, Activity, Settings,
  TrendingUp, BarChart2, History, BookOpen,
  Zap, Building2, LineChart, Shield,
  Sun, Moon, ChevronLeft, ChevronRight, X, LogOut
} from 'lucide-react'

/** Routes visible to all authenticated users */
const NAV_ITEMS = [
  { href: '/dashboard',            icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/predictions',          icon: Target,          label: 'Predictions' },
  { href: '/signals',              icon: Zap,             label: 'Signals' },
  { href: '/market-intelligence',  icon: TrendingUp,      label: 'Market Intelligence' },
  { href: '/news',                 icon: Newspaper,       label: 'News Feed' },
  { href: '/institutional-flows',  icon: Building2,       label: 'Institutional' },
  { href: '/options-intelligence', icon: LineChart,       label: 'Options' },
  { href: '/performance',          icon: BarChart2,       label: 'Performance' },
  { href: '/backtesting',          icon: History,         label: 'Backtesting' },
  { href: '/explanations',         icon: BookOpen,        label: 'Explanations' },
  { href: '/alerts',               icon: Bell,            label: 'Alerts' },
  { href: '/history',              icon: Activity,        label: 'History' },
  { href: '/settings',             icon: Settings,        label: 'Settings' },
]

/**
 * Admin-only routes — only rendered when isAdmin is true.
 * Mirrors the backend's require_admin guard on:
 *   - POST /api/v1/agents/run, /run/{agent_id}  → Agents tab
 *   - /api/v1/admin/*                            → Admin tab
 */
const ADMIN_ITEMS = [
  { href: '/agents', icon: Users,  label: 'Agents' },
  { href: '/admin',  icon: Shield, label: 'Admin' },
]

function SidebarBrand({ collapsed }) {
  return (
    <div className={`flex items-center ${collapsed ? 'justify-center' : 'gap-3'} min-w-0`}>
      <div
        className="flex items-center justify-center rounded-xl flex-shrink-0"
        style={{
          width: collapsed ? 32 : 36,
          height: collapsed ? 32 : 36,
          background: 'linear-gradient(135deg, #2A7A6F, #3A9E8F)',
        }}
      >
        <TrendingUp size={collapsed ? 16 : 18} color="#fff" />
      </div>
      {!collapsed && (
        <div className="min-w-0">
          <div style={{
            fontFamily: "'DM Sans', sans-serif",
            fontWeight: 800,
            fontSize: '17px',
            letterSpacing: '-0.02em',
            lineHeight: 1.15,
            whiteSpace: 'nowrap',
          }}>
            <span style={{ color: 'var(--text-primary)' }}>USA</span>
            <span style={{ color: 'var(--text-primary)', fontWeight: 400, fontSize: '15px', margin: '0 3px' }}>Swing</span>
          </div>
          <div style={{ fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '0.05em', marginTop: '1px' }}>
          </div>
        </div>
      )}
    </div>
  )
}

function NavLink({ href, icon: Icon, label, collapsed, onClose }) {
  const pathname = usePathname()
  const active = pathname === href || (href !== '/dashboard' && pathname.startsWith(href))
  return (
    <Link
      href={href}
      onClick={onClose}
      title={collapsed ? label : undefined}
      className={`
        flex items-center gap-3 rounded-xl mb-0.5
        font-medium transition-all duration-150
        ${active ? 'text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-800'}
        ${collapsed ? 'justify-center px-0 py-3' : 'px-3 py-2.5'}
      `}
      style={{
        background: active ? '#2A7A6F' : 'transparent',
        color: active ? '#fff' : 'var(--text-secondary)',
        fontSize: '14.5px',
      }}
    >
      <Icon size={17} style={{ flexShrink: 0 }} />
      {!collapsed && <span>{label}</span>}
    </Link>
  )
}

export default function Sidebar({ open, onClose, collapsed, onToggleCollapse }) {
  const { theme, toggleTheme } = useTheme()
  const { isAdmin, user, logout } = useAuth()

  return (
    <aside
      className={`
        fixed lg:static inset-y-0 left-0 z-50 flex flex-col
        transition-all duration-300
        ${open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        ${collapsed ? 'w-[64px]' : 'w-[232px]'}
        border-r
      `}
      style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
    >
      {/* Brand row */}
      <div
        className="flex items-center justify-between px-4 border-b flex-shrink-0"
        style={{ borderColor: 'var(--border)', height: '64px' }}
      >
        <SidebarBrand collapsed={collapsed} />
        <button
          onClick={onToggleCollapse}
          className="hidden lg:flex items-center justify-center w-7 h-7 rounded-lg
            hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex-shrink-0 ml-1"
          style={{ color: 'var(--text-muted)' }}
          aria-label="Toggle sidebar"
        >
          {collapsed ? <ChevronRight size={15} /> : <ChevronLeft size={15} />}
        </button>
        <button onClick={onClose} className="lg:hidden p-1" style={{ color: 'var(--text-secondary)' }}>
          <X size={18} />
        </button>
      </div>

      {/* Nav links */}
      <nav className="flex-1 overflow-y-auto py-3 px-2">
        {NAV_ITEMS.map((item) => (
          <NavLink key={item.href} {...item} collapsed={collapsed} onClose={onClose} />
        ))}

        {/* Admin-only links — Agents (trigger runs) + Admin — hidden from normal users */}
        {isAdmin && (
          <>
            <div
              className="mx-2 my-2 border-t"
              style={{ borderColor: 'var(--border)' }}
            />
            {ADMIN_ITEMS.map((item) => (
              <NavLink key={item.href} {...item} collapsed={collapsed} onClose={onClose} />
            ))}
          </>
        )}
      </nav>

      {/* Bottom bar: theme + logout */}
      <div className="border-t p-3 flex-shrink-0 space-y-1" style={{ borderColor: 'var(--border)' }}>
        <button
          onClick={toggleTheme}
          className={`
            w-full flex items-center gap-2.5 rounded-xl font-medium transition-all
            hover:bg-gray-100 dark:hover:bg-gray-800
            ${collapsed ? 'justify-center px-0 py-3' : 'px-3 py-2.5'}
          `}
          style={{ color: 'var(--text-secondary)', fontSize: '14.5px' }}
        >
          {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
          {!collapsed && <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>}
        </button>

        <button
          onClick={logout}
          title={collapsed ? 'Sign out' : undefined}
          className={`
            w-full flex items-center gap-2.5 rounded-xl font-medium transition-all
            hover:bg-red-50 dark:hover:bg-red-900/20
            ${collapsed ? 'justify-center px-0 py-3' : 'px-3 py-2.5'}
          `}
          style={{ color: '#B5451B', fontSize: '14.5px' }}
        >
          <LogOut size={17} />
          {!collapsed && <span>Sign Out</span>}
        </button>
      </div>
    </aside>
  )
}
