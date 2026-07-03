/**
 * File: frontend/src/components/layout/MainLayout.jsx
 * Main app shell — Sidebar + TopNav + TickerBar + content area.
 *
 * SPEC Section 7.3 — layout components
 */
'use client';
import { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import TopNav from './TopNav';
import TickerBar from './TickerBar';

export default function MainLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Keyboard shortcut Ctrl+K / Cmd+K — handled in GlobalSearchBar
  useEffect(() => {
    const handleKey = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        // Open search — TopNav handles this via state
        document.dispatchEvent(new CustomEvent('open-search'));
      }
    };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, []);

  return (
    <div className="flex flex-col h-screen overflow-hidden" style={{ background: 'var(--bg-primary)' }}>
      {/* Ticker strip — full page width, above sidebar + header */}
      <TickerBar />

      <div className="flex flex-1 overflow-hidden min-h-0">
        {/* Mobile sidebar overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-black/60 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <Sidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(c => !c)}
        />

        {/* Main content area */}
        <div className="flex-1 flex flex-col overflow-hidden min-w-0">
          <TopNav onMenuClick={() => setSidebarOpen(true)} />
          <main className="flex-1 overflow-y-auto">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
