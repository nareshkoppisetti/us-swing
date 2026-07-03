'use client';
import { Bell } from 'lucide-react';
const SEV_COLOR = { critical: 'text-red-400', warning: 'text-yellow-400', info: 'text-blue-400' };
export default function ActiveAlertsWidget({ alerts }) {
  const active = (alerts || []).filter(a => a.status === 'active');
  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Active Alerts</span>
        <Bell size={14} style={{ color: active.length > 0 ? '#eab308' : 'var(--text-muted)' }} />
      </div>
      <div className="text-3xl font-black" style={{ color: active.length > 0 ? '#eab308' : 'var(--text-muted)' }}>{active.length}</div>
      {active.length > 0 && (
        <div className="mt-2 space-y-1">
          {active.slice(0, 3).map(a => (
            <div key={a.id} className={`text-xs flex gap-1.5 ${SEV_COLOR[a.severity] || 'text-gray-400'}`}>
              <span>•</span>
              <span className="truncate">{a.message}</span>
            </div>
          ))}
        </div>
      )}
      {active.length === 0 && <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>No active alerts</p>}
    </div>
  );
}
