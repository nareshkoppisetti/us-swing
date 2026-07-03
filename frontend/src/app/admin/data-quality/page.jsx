'use client';
import { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';
import { api } from '@/lib/api';
import BackendPendingNotice from '@/components/admin/BackendPendingNotice';

export default function DataQualityPage() {
  const [quality, setQuality] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    api.getDataSources()
      .then(d => { if (d.success === false) setPending(true); else setQuality(d.data); })
      .catch(() => setPending(true))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(198,40,40,0.1)' }}>
          <Activity size={20} color="#B5451B" />
        </div>
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Data Quality</h1>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Validation pass rates and anomalies</p>
        </div>
      </div>

      {loading ? (
        <div className="rounded-xl border animate-pulse h-48" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
      ) : pending || !quality ? (
        <BackendPendingNotice module="Data quality monitoring" />
      ) : (
        <pre className="rounded-xl border p-4 text-xs overflow-auto" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>
          {JSON.stringify(quality, null, 2)}
        </pre>
      )}
    </div>
  );
}
