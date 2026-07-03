'use client';
import { useState, useEffect } from 'react';
import { Users } from 'lucide-react';
import { api } from '@/lib/api';
import { useAgentDefinitions } from '@/hooks/useAgents';
import BackendPendingNotice from '@/components/admin/BackendPendingNotice';

export default function AgentManagementPage() {
  const { agents, loading } = useAgentDefinitions();
  const [statusMap, setStatusMap] = useState({});
  const [pending, setPending] = useState(false);

  useEffect(() => {
    api.getAgentStatus()
      .then(d => {
        if (d.success === false) { setPending(true); return; }
        const map = {};
        (d.data || []).forEach(s => { map[s.agent_id] = s; });
        setStatusMap(map);
      })
      .catch(() => setPending(true));
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(198,40,40,0.1)' }}>
          <Users size={20} color="#B5451B" />
        </div>
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Agent Management</h1>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{agents.length} agents registered</p>
        </div>
      </div>

      {loading ? (
        <div className="rounded-xl border animate-pulse h-64" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
      ) : (
        <div className="rounded-xl border overflow-hidden" style={{ borderColor: 'var(--border)' }}>
          <table className="w-full text-sm">
            <thead style={{ background: 'var(--bg-secondary)' }}>
              <tr className="text-xs" style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>
                {['ID', 'Name', 'Category', 'Refresh', 'Dependencies', 'Status'].map(h => (
                  <th key={h} className="px-4 py-2.5 text-left font-semibold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody style={{ background: 'var(--bg-card)' }}>
              {agents.map(a => {
                const status = statusMap[a.agent_id];
                return (
                  <tr key={a.agent_id} className="border-b last:border-0" style={{ borderColor: 'var(--border)' }}>
                    <td className="px-4 py-2.5 font-mono text-xs" style={{ color: 'var(--text-muted)' }}>#{a.agent_id}</td>
                    <td className="px-4 py-2.5 font-medium" style={{ color: 'var(--text-primary)' }}>{a.agent_name}</td>
                    <td className="px-4 py-2.5" style={{ color: 'var(--text-secondary)' }}>{a.category || '—'}</td>
                    <td className="px-4 py-2.5 text-xs" style={{ color: 'var(--text-muted)' }}>{a.refresh_frequency || '—'}</td>
                    <td className="px-4 py-2.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                      {a.dependencies?.length > 0 ? a.dependencies.join(', ') : 'none'}
                    </td>
                    <td className="px-4 py-2.5">
                      {pending ? (
                        <span className="text-xs" style={{ color: 'var(--text-muted)' }}>—</span>
                      ) : status ? (
                        <span className={`text-xs font-semibold ${status.healthy ? 'text-green-400' : 'text-red-400'}`}>
                          {status.healthy ? '● Healthy' : '● Error'}
                        </span>
                      ) : (
                        <span className="text-xs" style={{ color: 'var(--text-muted)' }}>—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
