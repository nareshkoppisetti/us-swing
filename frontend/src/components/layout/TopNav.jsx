/**
 * File: frontend/src/components/layout/TopNav.jsx
 * Top navigation bar — logo, global search trigger, user info, theme toggle.
 *
 * SPEC Section 7.3 — Component Hierarchy (layout/)
 */
'use client';
import { useState } from 'react';
import Link from 'next/link';
import { Menu, Sun, Moon, LogOut, User, Bell, ChevronDown } from 'lucide-react';
import { useTheme } from '@/components/providers';
import { useAuth } from '@/hooks/useAuth';
import { useAlerts } from '@/hooks/useAlerts';

const SEV_COLOR = { critical: '#ef4444', warning: '#eab308', info: '#3b82f6' };

export default function TopNav({ onMenuClick }) {
  const { theme, toggleTheme } = useTheme();
  const { user, role, logout } = useAuth();
  const { alerts } = useAlerts({ status: 'active', page_size: 5 });
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [alertsOpen, setAlertsOpen] = useState(false);
  const activeAlerts = alerts || [];

  return (
    <>
      <header
        className="flex items-center justify-between px-4 h-14 flex-shrink-0 border-b"
        style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}
      >
        {/* Left — mobile menu + brand. The one search bar in the app lives
            on the dashboard page (full width), not here. */}
        <div className="flex items-center gap-3">
          <button
            className="lg:hidden p-1.5 rounded-md hover:bg-white/10 transition-colors"
            onClick={onMenuClick}
            aria-label="Open menu"
          >
            <Menu size={20} style={{ color: 'var(--text-secondary)' }} />
          </button>
        </div>

        {/* Right — theme, alerts, user */}
        <div className="flex items-center gap-1">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-white/10 transition-colors"
            title="Toggle theme"
          >
            {theme === 'dark'
              ? <Sun size={17} style={{ color: 'var(--text-secondary)' }} />
              : <Moon size={17} style={{ color: 'var(--text-secondary)' }} />
            }
          </button>

          {/* Alerts */}
          <div className="relative">
            <button
              className="p-2 rounded-lg hover:bg-white/10 transition-colors relative"
              onClick={() => setAlertsOpen(v => !v)}
              aria-label="Alerts"
            >
              <Bell size={17} style={{ color: 'var(--text-secondary)' }} />
              {activeAlerts.length > 0 && (
                <span
                  className="absolute top-0.5 right-0.5 flex items-center justify-center rounded-full text-[10px] font-bold text-white"
                  style={{ background: '#ef4444', minWidth: 15, height: 15, padding: '0 3px' }}
                >
                  {activeAlerts.length > 9 ? '9+' : activeAlerts.length}
                </span>
              )}
            </button>

            {alertsOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setAlertsOpen(false)} />
                <div
                  className="absolute right-0 top-10 z-50 w-80 rounded-xl border shadow-xl overflow-hidden"
                  style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
                >
                  <div className="px-3 py-2.5 border-b flex items-center justify-between" style={{ borderColor: 'var(--border)' }}>
                    <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Active Alerts</p>
                    <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{activeAlerts.length}</span>
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {activeAlerts.length === 0 ? (
                      <p className="px-3 py-6 text-sm text-center" style={{ color: 'var(--text-muted)' }}>
                        No active alerts
                      </p>
                    ) : (
                      activeAlerts.map(a => (
                        <div
                          key={a.id}
                          className="px-3 py-2.5 border-b last:border-b-0 flex gap-2"
                          style={{ borderColor: 'var(--border)' }}
                        >
                          <span
                            className="mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0"
                            style={{ background: SEV_COLOR[a.severity] || 'var(--text-muted)' }}
                          />
                          <div className="min-w-0">
                            <p className="text-sm truncate" style={{ color: 'var(--text-primary)' }}>
                              {a.message || `${a.symbol ?? ''} alert`}
                            </p>
                            {a.symbol && (
                              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{a.symbol}</p>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                  <Link
                    href="/alerts"
                    onClick={() => setAlertsOpen(false)}
                    className="block px-3 py-2.5 text-center text-sm font-medium hover:bg-white/5 transition-colors border-t"
                    style={{ borderColor: 'var(--border)', color: '#2A7A6F' }}
                  >
                    View all alerts
                  </Link>
                </div>
              </>
            )}
          </div>

          {/* User menu */}
          <div className="relative ml-1">
            <button
              className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-white/10 transition-colors"
              onClick={() => setUserMenuOpen(v => !v)}
            >
              <div
                className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ background: '#2A7A6F' }}
              >
                <User size={15} color="#fff" />
              </div>
              <span className="hidden md:block text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                {user?.username || 'User'}
              </span>
              <ChevronDown size={13} style={{ color: 'var(--text-muted)' }} />
            </button>

            {userMenuOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
                <div
                  className="absolute right-0 top-10 z-50 w-44 rounded-xl border py-1 shadow-xl"
                  style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
                >
                  <div className="px-3 py-2 border-b" style={{ borderColor: 'var(--border)' }}>
                    <p className="text-xs font-medium" style={{ color: 'var(--text-primary)' }}>{user?.username}</p>
                    <p className="text-xs capitalize" style={{ color: 'var(--text-muted)' }}>{role?.replace('_', ' ') ?? 'Viewer'}</p>
                  </div>
                  <button
                    onClick={logout}
                    className="flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-red-500/10 transition-colors text-red-400"
                  >
                    <LogOut size={14} />
                    Sign out
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </header>
    </>
  );
}
