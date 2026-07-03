'use client';
import { useState, useEffect } from 'react';
import { BarChart2 } from 'lucide-react';
import { api } from '@/lib/api';
import BackendPendingNotice from '@/components/admin/BackendPendingNotice';

export default function ModelMonitoringPage() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    api.getModelPerformance()
      .then(d => { if (d.success === false) setPending(true); else setModels(d.data || []); })
      .catch(() => setPending(true))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(198,40,40,0.1)' }}>
          <BarChart2 size={20} color="#B5451B" />
        </div>
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Model Monitoring</h1>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>ML ensemble model performance by horizon</p>
        </div>
      </div>

      {loading ? (
        <div className="rounded-xl border animate-pulse h-48" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
      ) : pending ? (
        <BackendPendingNotice module="Model performance monitoring" />
      ) : models.length === 0 ? (
        <div className="rounded-xl border p-10 text-center" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
          No model performance data yet
        </div>
      ) : (
        <div className="rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
          <table className="w-full text-sm">
            <thead style={{ background: 'var(--bg-secondary)' }}>
              <tr className="text-xs" style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>
                {['Horizon', 'Model', 'Accuracy', 'Last Trained', 'Status'].map(h => (
                  <th key={h} className="px-4 py-2.5 text-left font-semibold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody style={{ background: 'var(--bg-card)' }}>
              {models.map((m, i) => (
                <tr key={i} className="border-b last:border-0" style={{ borderColor: 'var(--border)' }}>
                  <td className="px-4 py-2.5 font-semibold" style={{ color: 'var(--text-primary)' }}>{m.horizon_days}D</td>
                  <td className="px-4 py-2.5" style={{ color: 'var(--text-secondary)' }}>{m.model_name}</td>
                  <td className="px-4 py-2.5">
                    <span className={(m.accuracy || 0) >= 0.55 ? 'text-green-400' : 'text-yellow-400'}>
                      {((m.accuracy || 0) * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                    {m.last_trained ? new Date(m.last_trained).toLocaleDateString() : '—'}
                  </td>
                  <td className="px-4 py-2.5">
                    <span className={m.is_active ? 'text-green-400 text-xs' : 'text-gray-500 text-xs'}>
                      {m.is_active ? '● Active' : 'Inactive'}
                    </span>
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
