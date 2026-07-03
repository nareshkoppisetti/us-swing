'use client';
/**
 * File: frontend/src/app/alerts/page.jsx
 * Alert management — list active/acknowledged/all alerts, create new ones.
 * Integrates with backend /api/v1/alerts/ endpoints.
 */
import { useState, useEffect, useCallback } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { Bell, CheckCircle, RefreshCw, Plus, X, TrendingUp, TrendingDown, Zap } from 'lucide-react';

const SEV_STYLE = {
  critical: 'border-l-red-500 ',
  warning:  'border-l-yellow-500',
  info:     'border-l-blue-500',
  high:     'border-l-red-500',
  medium:   'border-l-yellow-500',
  low:      'border-l-blue-500',
};
const SEV_BADGE = {
  critical: 'text-red-400 bg-red-400/10 border-red-400/30',
  warning:  'text-yellow-400 bg-yellow-400/10 border-yellow-400/30',
  info:     'text-blue-400 bg-blue-400/10 border-blue-400/30',
};

function AlertCard({ alert, onAcknowledge }) {
  const dir = alert.direction || alert.signal || '';
  const sev = alert.severity || 'info';
  const isUp = dir === 'Bullish' || dir === 'bull';
  const isDown = dir === 'Bearish' || dir === 'bear';

  return (
    <div className={`rounded-xl border-l-4 p-4 ${SEV_STYLE[sev] || 'border-l-gray-500'}`}
      style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderLeftWidth: '4px' }}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            {alert.symbol && (
              <span className="font-mono font-bold text-sm" style={{ color: 'var(--text-primary)' }}>
                {alert.symbol}
              </span>
            )}
            {alert.timeframe && (
              <span className="text-xs px-1.5 py-0.5 rounded font-medium"
                style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)' }}>
                {alert.timeframe}
              </span>
            )}
            {dir && (
              <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border font-semibold
                ${isUp ? 'text-green-400 bg-green-400/10 border-green-400/30' :
                  isDown ? 'text-red-400 bg-red-400/10 border-red-400/30' :
                  'text-yellow-400 bg-yellow-400/10 border-yellow-400/30'}`}>
                {isUp ? <TrendingUp size={10} /> : isDown ? <TrendingDown size={10} /> : null}
                {dir}
              </span>
            )}
            {(alert.accuracy_score >= 80 || alert.confidence >= 80) && (
              <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border font-semibold text-yellow-300 bg-yellow-300/10 border-yellow-300/30">
                <Zap size={9} />HIGH CONF
              </span>
            )}
            <span className={`text-xs px-2 py-0.5 rounded-full border font-semibold ${SEV_BADGE[sev] || SEV_BADGE.info}`}>
              {sev}
            </span>
          </div>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            {alert.message || alert.title || 'No message'}
          </p>
          {alert.created_at && (
            <p className="text-xs mt-1.5" style={{ color: 'var(--text-muted)' }}>
              {new Date(alert.created_at).toLocaleString()}
            </p>
          )}
        </div>
        {alert.status === 'active' && onAcknowledge && (
          <button onClick={() => onAcknowledge(alert.id)}
            className="flex-shrink-0 p-1.5 rounded-lg hover:bg-green-500/20 transition-colors text-green-400"
            title="Acknowledge">
            <CheckCircle size={16} />
          </button>
        )}
        {alert.status !== 'active' && (
          <span className="text-xs text-green-400 flex-shrink-0">✓ ACK</span>
        )}
      </div>
    </div>
  );
}

function CreateAlertModal({ onClose, onCreated }) {
  const [form, setForm] = useState({ symbol: 'SPY', message: '', severity: 'info', alert_type: 'manual' });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.message.trim()) { setError('Message is required'); return; }
    setSaving(true); setError(null);
    try {
      await api.createAlert(form);
      onCreated();
      onClose();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="rounded-2xl border p-6 w-full max-w-md"
        style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-bold" style={{ color: 'var(--text-primary)' }}>Create Alert</h2>
          <button onClick={onClose}><X size={18} style={{ color: 'var(--text-muted)' }} /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          {[
            { label: 'Symbol', field: 'symbol', type: 'text', placeholder: 'e.g. AAPL' },
            { label: 'Message', field: 'message', type: 'text', placeholder: 'Alert description' },
          ].map(({ label, field, ...rest }) => (
            <div key={field}>
              <label className="text-xs font-semibold mb-1 block" style={{ color: 'var(--text-muted)' }}>{label}</label>
              <input {...rest}
                value={form[field]} onChange={e => setForm(p => ({ ...p, [field]: e.target.value }))}
                className="w-full rounded-lg border px-3 py-2 text-sm outline-none"
                style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}
              />
            </div>
          ))}
          <div>
            <label className="text-xs font-semibold mb-1 block" style={{ color: 'var(--text-muted)' }}>Severity</label>
            <select value={form.severity} onChange={e => setForm(p => ({ ...p, severity: e.target.value }))}
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none"
              style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              {['info', 'warning', 'critical'].map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          {error && <p className="text-xs text-red-400">{error}</p>}
          <div className="flex gap-2 pt-1">
            <button type="button" onClick={onClose}
              className="flex-1 py-2 rounded-xl text-sm border transition-colors"
              style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}>
              Cancel
            </button>
            <button type="submit" disabled={saving}
              className="flex-1 py-2 rounded-xl text-sm font-semibold text-white disabled:opacity-50"
              style={{ background: '#2A7A6F' }}>
              {saving ? 'Saving…' : 'Create Alert'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const FILTER_TABS = ['all', 'active', 'acknowledged'];

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [showCreate, setShowCreate] = useState(false);
  const [error, setError] = useState(null);

  const fetchAlerts = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      const res = await api.getAlerts(params);
      setAlerts(res.data || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => { fetchAlerts(); }, [fetchAlerts]);

  const acknowledge = async (id) => {
    try {
      await api.acknowledgeAlert(id);
      setAlerts(prev => prev.map(a => a.id === id ? { ...a, status: 'acknowledged' } : a));
    } catch (e) { setError(e.message); }
  };

  const activeCount = alerts.filter(a => a.status === 'active').length;

  return (
    <MainLayout>
      <div className="p-4 md:p-6 space-y-5">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: 'rgba(42,122,111,0.12)' }}>
              <Bell size={20} color="#2A7A6F" />
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Alert Engine</h1>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {activeCount} active alert{activeCount !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex rounded-xl overflow-hidden border" style={{ borderColor: 'var(--border)' }}>
              {FILTER_TABS.map(f => (
                <button key={f} onClick={() => setFilter(f)}
                  className="px-3 py-2 text-xs font-semibold transition-colors capitalize"
                  style={{
                    background: filter === f ? '#2A7A6F' : 'var(--bg-card)',
                    color: filter === f ? '#fff' : 'var(--text-secondary)',
                  }}>{f}</button>
              ))}
            </div>
            <button onClick={fetchAlerts}
              className="p-2 rounded-xl border hover:bg-white/5 transition-colors"
              style={{ borderColor: 'var(--border)' }}>
              <RefreshCw size={14} style={{ color: 'var(--text-muted)' }} />
            </button>
            <button onClick={() => setShowCreate(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white"
              style={{ background: '#2A7A6F' }}>
              <Plus size={14} />New Alert
            </button>
          </div>
        </div>

        {error && (
          <div className="rounded-xl border border-red-500/30 p-4 text-sm text-red-400">
            {error}
          </div>
        )}

        {loading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="rounded-xl border animate-pulse h-20"
                style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
            ))}
          </div>
        ) : alerts.length === 0 ? (
          <div className="rounded-xl border p-16 text-center"
            style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
            <Bell size={44} className="mx-auto mb-4 opacity-30" />
            <p className="text-base font-semibold mb-2">No alerts</p>
            <p className="text-sm">Alerts are generated automatically or manually</p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert, i) => (
              <AlertCard key={alert.id || i} alert={alert}
                onAcknowledge={alert.status === 'active' ? acknowledge : null} />
            ))}
          </div>
        )}
      </div>
      {showCreate && (
        <CreateAlertModal onClose={() => setShowCreate(false)} onCreated={fetchAlerts} />
      )}
    </MainLayout>
  );
}
