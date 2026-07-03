'use client';
import { useState, useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import { api } from '@/lib/api';
import BackendPendingNotice from '@/components/admin/BackendPendingNotice';

export default function AdminAlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    api.getAlerts({ page_size: 50 })
      .then(d => { if (d.success === false) setPending(true); else setAlerts(d.data || []); })
      .catch(() => setPending(true))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(198,40,40,0.1)' }}>
          <AlertTriangle size={20} color="#B5451B" />
        </div>
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Alert Engine (Admin)</h1>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>System-wide alert monitoring</p>
        </div>
      </div>

      {loading ? (
        <div className="rounded-xl border animate-pulse h-48" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
      ) : pending ? (
        <BackendPendingNotice module="Alert engine" />
      ) : alerts.length === 0 ? (
        <div className="rounded-xl border p-10 text-center" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
          No alerts in the system
        </div>
      ) : (
        <div className="rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
          <table className="w-full text-sm">
            <thead style={{ background: 'var(--bg-secondary)' }}>
              <tr className="text-xs" style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>
                {['Symbol', 'Severity', 'Status', 'Message', 'Created'].map(h => (
                  <th key={h} className="px-4 py-2.5 text-left font-semibold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody style={{ background: 'var(--bg-card)' }}>
              {alerts.map((a, i) => (
                <tr key={a.id || i} className="border-b last:border-0" style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-2.5 font-mono" style={{ color: 'var(--text-primary)' }}>{a.symbol || '—'}</td>
                  <td className="px-4 py-2.5 capitalize" style={{ color: 'var(--text-secondary)' }}>{a.severity}</td>
                  <td className="px-4 py-2.5">
                    <span className={a.status === 'active' ? 'text-yellow-400' : 'text-green-400'}>{a.status}</span>
                  </td>
                  <td className="px-4 py-2.5" style={{ color: 'var(--text-secondary)' }}>{a.message}</td>
                  <td className="px-4 py-2.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                    {a.created_at ? new Date(a.created_at).toLocaleString() : '—'}
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
