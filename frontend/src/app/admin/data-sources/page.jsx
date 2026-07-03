'use client';
import { useState, useEffect } from 'react';
import { Database } from 'lucide-react';
import { api } from '@/lib/api';
import BackendPendingNotice from '@/components/admin/BackendPendingNotice';

export default function DataSourcesPage() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    api.getDataSources()
      .then(d => { if (d.success === false) setPending(true); else setSources(d.data || []); })
      .catch(() => setPending(true))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(198,40,40,0.1)' }}>
          <Database size={20} color="#B5451B" />
        </div>
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Data Sources</h1>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Collector health and freshness</p>
        </div>
      </div>

      {loading ? (
        <div className="rounded-xl border animate-pulse h-48" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
      ) : pending ? (
        <BackendPendingNotice module="Data source monitoring" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sources.map((s, i) => (
            <div key={i} className="rounded-xl border p-4" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{s.name}</span>
                <span className={`w-2 h-2 rounded-full ${s.healthy ? 'bg-green-400' : 'bg-red-400'}`} />
              </div>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                Last fetch: {s.last_fetch ? new Date(s.last_fetch).toLocaleString() : 'Never'}
              </p>
              {s.error_count != null && (
                <p className="text-xs mt-1" style={{ color: s.error_count > 0 ? '#ef4444' : 'var(--text-muted)' }}>
                  Errors (24h): {s.error_count}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
