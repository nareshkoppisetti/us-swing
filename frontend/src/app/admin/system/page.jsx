'use client';
import { useState, useEffect } from 'react';
import { Monitor, Cpu, Database, Server } from 'lucide-react';
import { api } from '@/lib/api';
import BackendPendingNotice from '@/components/admin/BackendPendingNotice';

function MetricCard({ icon: Icon, label, value, unit = '' }) {
  return (
    <div className="rounded-xl border p-4" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center gap-2 mb-2">
        <Icon size={14} color="#B5451B" />
        <span className="text-xs font-semibold" style={{ color: 'var(--text-muted)' }}>{label}</span>
      </div>
      <p className="text-2xl font-black" style={{ color: 'var(--text-primary)' }}>{value ?? '—'}{unit}</p>
    </div>
  );
}

export default function SystemStatusPage() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    api.getSystemMetrics()
      .then(d => { if (d.success === false) setPending(true); else setMetrics(d.data); })
      .catch(() => setPending(true))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(198,40,40,0.1)' }}>
          <Monitor size={20} color="#B5451B" />
        </div>
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>System Status</h1>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Infrastructure health and resource usage</p>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="rounded-xl border animate-pulse h-24" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />)}
        </div>
      ) : pending ? (
        <BackendPendingNotice module="System monitoring" />
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard icon={Cpu} label="CPU Usage" value={metrics?.cpu_pct} unit="%" />
          <MetricCard icon={Server} label="Memory" value={metrics?.memory_pct} unit="%" />
          <MetricCard icon={Database} label="DB Connections" value={metrics?.db_connections} />
          <MetricCard icon={Monitor} label="Uptime" value={metrics?.uptime_hours} unit="h" />
        </div>
      )}
    </div>
  );
}
