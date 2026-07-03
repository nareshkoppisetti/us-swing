'use client';
import { useState, useEffect } from 'react';
import { Server } from 'lucide-react';
import { api } from '@/lib/api';
import BackendPendingNotice from '@/components/admin/BackendPendingNotice';

export default function ApiHealthPage() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    api.getApiHealth()
      .then(d => { if (d.success === false) setPending(true); else setHealth(d.data); })
      .catch(() => setPending(true))
      .finally(() => setLoading(false));
  }, []);

  const endpoints = health?.endpoints || [];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(198,40,40,0.1)' }}>
          <Server size={20} color="#B5451B" />
        </div>
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>API Health</h1>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Endpoint latency and error rates</p>
        </div>
      </div>

      {loading ? (
        <div className="rounded-xl border animate-pulse h-48" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
      ) : pending ? (
        <BackendPendingNotice module="API health monitoring" />
      ) : endpoints.length === 0 ? (
        <div className="rounded-xl border p-10 text-center" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
          No endpoint health data yet
        </div>
      ) : (
        <div className="rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
          <table className="w-full text-sm">
            <thead style={{ background: 'var(--bg-secondary)' }}>
              <tr className="text-xs" style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>
                {['Endpoint', 'Avg Latency', 'Error Rate', 'Status'].map(h => (
                  <th key={h} className="px-4 py-2.5 text-left font-semibold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody style={{ background: 'var(--bg-card)' }}>
              {endpoints.map((e, i) => (
                <tr key={i} className="border-b last:border-0" style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-2.5 font-mono text-xs" style={{ color: 'var(--text-primary)' }}>{e.path}</td>
                  <td className="px-4 py-2.5" style={{ color: 'var(--text-secondary)' }}>{e.avg_latency_ms}ms</td>
                  <td className="px-4 py-2.5" style={{ color: e.error_rate > 0.05 ? '#ef4444' : 'var(--text-secondary)' }}>
                    {(e.error_rate * 100).toFixed(2)}%
                  </td>
                  <td className="px-4 py-2.5">
                    <span className={e.healthy ? 'text-green-400' : 'text-red-400'}>{e.healthy ? '● OK' : '● Degraded'}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
