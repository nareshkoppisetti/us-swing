'use client';
import { useState, useEffect } from 'react';
import { FileText, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api';
import BackendPendingNotice from '@/components/admin/BackendPendingNotice';

const LEVEL_COLOR = { error: 'text-red-400', warning: 'text-yellow-400', info: 'text-blue-400', debug: 'text-gray-500' };

export default function LogsPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);
  const [level, setLevel] = useState('');

  const load = () => {
    setLoading(true);
    api.getLogs(level ? { level } : {})
      .then(d => { if (d.success === false) setPending(true); else setLogs(d.data || []); })
      .catch(() => setPending(true))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [level]);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(198,40,40,0.1)' }}>
            <FileText size={20} color="#B5451B" />
          </div>
          <div>
            <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>System Logs</h1>
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{logs.length} entries</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <select value={level} onChange={e => setLevel(e.target.value)}
            className="text-sm rounded-xl border px-3 py-2 outline-none"
            style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
            {['', 'error', 'warning', 'info', 'debug'].map(l => <option key={l} value={l}>{l || 'All levels'}</option>)}
          </select>
          <button onClick={load} className="p-2 rounded-xl border hover:bg-white/5" style={{ borderColor: 'var(--border)' }}>
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} style={{ color: 'var(--text-muted)' }} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="rounded-xl border animate-pulse h-64" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
      ) : pending ? (
        <BackendPendingNotice module="Log aggregation" />
      ) : (
        <div className="rounded-xl border p-4 font-mono text-xs space-y-1 max-h-[600px] overflow-y-auto"
          style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
          {logs.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No logs found</p>
          ) : logs.map((l, i) => (
            <div key={i} className="flex gap-2">
              <span style={{ color: 'var(--text-muted)' }}>{l.timestamp ? new Date(l.timestamp).toLocaleTimeString() : ''}</span>
              <span className={`font-semibold ${LEVEL_COLOR[l.level] || ''}`}>[{l.level?.toUpperCase()}]</span>
              <span style={{ color: 'var(--text-secondary)' }}>{l.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
