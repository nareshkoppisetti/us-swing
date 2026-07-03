'use client';
/**
 * File: frontend/src/app/explanations/page.jsx
 * AI-generated explanation browser — per symbol, with history.
 */
import { useState, useEffect, useCallback } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { BookOpen, RefreshCw, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';

const SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA', 'AMZN', 'META', 'MSFT', 'GOOGL', 'GLD'];

function ExplanationCard({ explanation, expanded, onToggle }) {
  const pred = explanation?.prediction_summary;
  const dir = pred?.direction || explanation?.direction;
  const isUp = dir === 'Bullish'; const isDown = dir === 'Bearish';

  return (
    <div className="rounded-xl border overflow-hidden" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-start justify-between gap-3 p-4 cursor-pointer" onClick={onToggle}>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="font-mono font-bold text-sm" style={{ color: 'var(--text-primary)' }}>
              {explanation?.symbol}
            </span>
            {dir && (
              <span className={`text-xs px-2 py-0.5 rounded-full border font-semibold
                ${isUp ? 'text-green-400 bg-green-400/10 border-green-400/30' :
                  isDown ? 'text-red-400 bg-red-400/10 border-red-400/30' :
                  'text-yellow-400 bg-yellow-400/10 border-yellow-400/30'}`}>
                {dir}
              </span>
            )}
            {pred?.confidence != null && (
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {pred.confidence.toFixed(0)}% confidence
              </span>
            )}
            {explanation?.horizon_days && (
              <span className="text-xs px-1.5 py-0.5 rounded" style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)' }}>
                {explanation.horizon_days}D
              </span>
            )}
          </div>
          <p className={`text-sm ${expanded ? '' : 'line-clamp-2'}`} style={{ color: 'var(--text-secondary)' }}>
            {explanation?.narrative_text || explanation?.explanation_text || explanation?.text || 'No narrative available.'}
          </p>
          {explanation?.created_at && (
            <p className="text-xs mt-1.5" style={{ color: 'var(--text-muted)' }}>
              {new Date(explanation.created_at).toLocaleString()}
            </p>
          )}
        </div>
        <div className="flex-shrink-0 p-1" style={{ color: 'var(--text-muted)' }}>
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>

      {expanded && explanation?.key_factors?.length > 0 && (
        <div className="px-4 pb-4 border-t pt-3" style={{ borderColor: 'var(--border)' }}>
          <p className="text-xs font-semibold mb-2" style={{ color: 'var(--text-muted)' }}>KEY FACTORS</p>
          <div className="space-y-1.5">
            {explanation.key_factors.map((f, i) => (
              <div key={i} className="flex items-start gap-2 text-xs">
                <span className={`flex-shrink-0 mt-0.5 ${f.direction === 'bullish' ? 'text-green-400' : f.direction === 'bearish' ? 'text-red-400' : 'text-yellow-400'}`}>•</span>
                <span style={{ color: 'var(--text-secondary)' }}>{f.factor || f.text || String(f)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function ExplanationsPage() {
  const [symbol, setSymbol] = useState('SPY');
  const [explanations, setExplanations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [expandedId, setExpandedId] = useState(null);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);

  const load = useCallback(async () => {
    if (!symbol) return;
    setLoading(true); setError(null);
    try {
      const res = await api.getExplanationHistory(symbol, page, 20);
      setExplanations(res.data || []);
    } catch (e) {
      setError(e.message);
      // Try latest explanation as fallback
      try {
        const latest = await api.getLatestExplanation(symbol);
        if (latest.data) setExplanations([latest.data]);
      } catch {}
    } finally {
      setLoading(false);
    }
  }, [symbol, page]);

  useEffect(() => { load(); }, [load]);

  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      // Get latest prediction ID first
      const pred = await api.getPrediction(symbol);
      const predId = pred?.data?.id;
      if (predId) {
        await api.regenerateExplanation(predId);
        await load();
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setRegenerating(false);
    }
  };

  return (
    <MainLayout>
      <div className="p-4 md:p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: 'rgba(42,122,111,0.12)' }}>
              <BookOpen size={20} color="#2A7A6F" />
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>AI Explanations</h1>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>LLM-generated analyst narratives</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <select value={symbol} onChange={e => { setSymbol(e.target.value); setPage(1); }}
              className="text-sm rounded-xl border px-3 py-2 outline-none"
              style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              {SYMBOLS.map(s => <option key={s}>{s}</option>)}
            </select>
            <button onClick={handleRegenerate} disabled={regenerating}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white disabled:opacity-50"
              style={{ background: '#2A7A6F' }}>
              <Sparkles size={13} className={regenerating ? 'animate-spin' : ''} />
              Regenerate
            </button>
            <button onClick={load} disabled={loading}
              className="p-2 rounded-xl border hover:bg-white/5" style={{ borderColor: 'var(--border)' }}>
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} style={{ color: 'var(--text-muted)' }} />
            </button>
          </div>
        </div>

        {error && (
          <div className="rounded-xl border border-red-500/30 p-4 text-sm text-red-400">{error}</div>
        )}

        {loading ? (
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="rounded-xl border animate-pulse h-28"
                style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
            ))}
          </div>
        ) : explanations.length === 0 ? (
          <div className="rounded-xl border p-14 text-center"
            style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
            <BookOpen size={44} className="mx-auto mb-4 opacity-30" />
            <p className="text-base font-semibold mb-2">No explanations yet</p>
            <p className="text-sm mb-4">Generate a prediction for {symbol} first</p>
            <button onClick={handleRegenerate} disabled={regenerating}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white"
              style={{ background: '#2A7A6F' }}>
              <Sparkles size={13} />Generate Explanation
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {explanations.map((e, i) => (
              <ExplanationCard key={e.id || i} explanation={e}
                expanded={expandedId === (e.id || i)}
                onToggle={() => setExpandedId(expandedId === (e.id || i) ? null : (e.id || i))}
              />
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
