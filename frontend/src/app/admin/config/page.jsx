'use client';
import { useState } from 'react';
import { Settings, Save } from 'lucide-react';
import { useSystemConfig } from '@/hooks/useAdmin';
import BackendPendingNotice from '@/components/admin/BackendPendingNotice';

export default function SystemConfigPage() {
  const { config, loading, saving, save } = useSystemConfig();
  const [form, setForm] = useState(null);
  const pending = !loading && !config;

  const effective = form || config || {};

  const handleChange = (key, value) => setForm(p => ({ ...(p || config || {}), [key]: value }));
  const handleSave = () => form && save(form);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(198,40,40,0.1)' }}>
            <Settings size={20} color="#B5451B" />
          </div>
          <div>
            <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>System Config</h1>
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Platform-wide settings</p>
          </div>
        </div>
        {config && (
          <button onClick={handleSave} disabled={saving || !form}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white disabled:opacity-50"
            style={{ background: '#B5451B' }}>
            <Save size={14} />{saving ? 'Saving…' : 'Save Changes'}
          </button>
        )}
      </div>

      {loading ? (
        <div className="rounded-xl border animate-pulse h-48" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
      ) : pending ? (
        <BackendPendingNotice module="System configuration" />
      ) : (
        <div className="rounded-xl border p-5 space-y-4" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
          {Object.entries(effective).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between gap-4">
              <label className="text-sm font-medium capitalize" style={{ color: 'var(--text-secondary)' }}>
                {key.replace(/_/g, ' ')}
              </label>
              {typeof value === 'boolean' ? (
                <input type="checkbox" checked={value} onChange={e => handleChange(key, e.target.checked)} />
              ) : (
                <input
                  value={value ?? ''}
                  onChange={e => handleChange(key, e.target.value)}
                  className="rounded-lg border px-3 py-1.5 text-sm outline-none w-48"
                  style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}
                />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
