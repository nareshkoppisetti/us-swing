'use client';
/**
 * File: frontend/src/app/admin/page.jsx
 * Admin overview — system health snapshot, quick stats.
 */
import { useState, useEffect } from 'react';
import { LayoutDashboard, Users, Brain, Activity, AlertTriangle } from 'lucide-react';
import { api } from '@/lib/api';
import BackendPendingNotice from '@/components/admin/BackendPendingNotice';

function StatCard({ icon: Icon, label, value, color = '#B5451B' }) {
  return (
    <div className="rounded-xl border p-4" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center gap-2 mb-2">
        <Icon size={14} color={color} />
        <span className="text-xs font-semibold" style={{ color: 'var(--text-muted)' }}>{label}</span>
      </div>
      <p className="text-2xl font-black" style={{ color: 'var(--text-primary)' }}>{value ?? '—'}</p>
    </div>
  );
}

export default function AdminOverviewPage() {
  const [metrics, setMetrics] = useState(null);
  const [pending, setPending] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSystemMetrics()
      .then(d => {
        if (d.success === false) setPending(true);
        else setMetrics(d.data);
      })
      .catch(() => setPending(true))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(198,40,40,0.1)' }}>
          <LayoutDashboard size={20} color="#B5451B" />
        </div>
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Admin Overview</h1>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Platform health and key metrics</p>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="rounded-xl border animate-pulse h-24" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
          ))}
        </div>
      ) : pending ? (
        <BackendPendingNotice module="Admin system metrics" />
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard icon={Users} label="Active Users" value={metrics?.active_users} />
          <StatCard icon={Brain} label="Predictions Today" value={metrics?.predictions_today} />
          <StatCard icon={Activity} label="Agent Runs Today" value={metrics?.agent_runs_today} />
          <StatCard icon={AlertTriangle} label="Active Alerts" value={metrics?.active_alerts} />
        </div>
      )}
    </div>
  );
}
