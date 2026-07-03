/**
 * File: frontend/src/components/search/SymbolDetailPanel.jsx
 * Full-page overlay showing complete symbol analysis.
 *
 * SPEC Section 7.4 — SymbolDetailPanel Sections
 * BUILD_PLAN Phase 13.3
 */
'use client';
import { useState, useEffect } from 'react';
import { X, ArrowLeft, RefreshCw, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { useQuote } from '@/hooks/useMarketData';
import { useAgentResults } from '@/hooks/useAgents';
import { useSymbolPredictions, useGeneratePrediction } from '@/hooks/usePredictions';
import { useWebSocket } from '@/hooks/useWebSocket';
import { signalBg, formatPct, formatCurrency } from '@/lib/utils';

function DirectionIcon({ direction, size = 16 }) {
  if (direction === 'Bullish') return <TrendingUp size={size} className="text-green-400" />;
  if (direction === 'Bearish') return <TrendingDown size={size} className="text-red-400" />;
  return <Minus size={size} className="text-yellow-400" />;
}

function PredCard({ pred }) {
  if (!pred) return null;
  const up = pred.direction === 'Bullish';
  const down = pred.direction === 'Bearish';
  return (
    <div
      className="rounded-xl border p-4 flex-shrink-0 w-44"
      style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-bold" style={{ color: 'var(--text-muted)' }}>{pred.horizon_days}D</span>
        <DirectionIcon direction={pred.direction} size={14} />
      </div>
      <div className={`text-sm font-bold mb-1 ${up ? 'text-green-400' : down ? 'text-red-400' : 'text-yellow-400'}`}>
        {pred.direction}
      </div>
      <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
        Confidence: <span style={{ color: 'var(--text-primary)' }}>{pred.confidence?.toFixed(0)}%</span>
      </div>
      <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
        Risk: <span style={{ color: 'var(--text-primary)' }}>{pred.risk_score?.toFixed(0)}</span>
      </div>
      {pred.expected_move_pct != null && (
        <div className={`text-xs mt-1 font-medium ${pred.expected_move_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {formatPct(pred.expected_move_pct)}
        </div>
      )}
    </div>
  );
}

function AgentRow({ agent }) {
  const up = agent.signal === 'Bullish';
  const down = agent.signal === 'Bearish';
  return (
    <div className="flex items-center gap-3 py-2 border-b last:border-0" style={{ borderColor: 'var(--border)' }}>
      <span className="text-xs font-mono w-6 text-center flex-shrink-0" style={{ color: 'var(--text-muted)' }}>
        {agent.agent_id}
      </span>
      <div className="flex-1 min-w-0">
        <div className="text-xs font-medium truncate" style={{ color: 'var(--text-primary)' }}>{agent.agent_name}</div>
        {agent.reasoning && (
          <div className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>{agent.reasoning}</div>
        )}
      </div>
      <span className={`text-xs font-semibold flex-shrink-0 ${up ? 'text-green-400' : down ? 'text-red-400' : 'text-yellow-400'}`}>
        {agent.signal}
      </span>
      <span className="text-xs w-10 text-right flex-shrink-0" style={{ color: 'var(--text-secondary)' }}>
        {agent.score?.toFixed(0)}
      </span>
    </div>
  );
}

export default function SymbolDetailPanel({ symbol, generating, onClose, onBack }) {
  const ticker = symbol?.ticker || symbol?.symbol || symbol;
  const { quote, loading: quoteLoading } = useQuote(ticker);
  const { results: agentResults, loading: agentsLoading } = useAgentResults(ticker);
  const { predictions, loading: predsLoading } = useSymbolPredictions(ticker);
  const [explanation, setExplanation] = useState(null);
  const { subscribe } = useWebSocket();

  // Listen for explanation_ready via WebSocket
  useEffect(() => {
    if (!ticker) return;
    const unsub = subscribe('explanation_ready', (data) => {
      if (data.symbol === ticker) {
        setExplanation(data.narrative_text || data.explanation);
      }
    });
    return unsub;
  }, [ticker, subscribe]);

  const HORIZONS = [2, 5, 10, 20, 30, 60];
  const predsByHorizon = {};
  (predictions || []).forEach(p => { predsByHorizon[p.horizon_days] = p; });

  const displayName = symbol?.name || ticker;
  const price = quote?.price;
  const changePct = quote?.change_pct;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden" style={{ background: 'var(--bg-primary)' }}>
      {/* Header */}
      <div
        className="flex items-center gap-3 px-5 py-3 border-b"
        style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}
      >
        <button
          onClick={onBack || onClose}
          className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
        >
          <ArrowLeft size={18} style={{ color: 'var(--text-secondary)' }} />
        </button>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3">
            <span className="font-mono font-bold text-lg" style={{ color: 'var(--text-primary)' }}>
              {ticker}
            </span>
            <span className="text-sm truncate" style={{ color: 'var(--text-muted)' }}>{displayName}</span>
          </div>
          {!quoteLoading && price != null && (
            <div className="flex items-center gap-2 text-sm">
              <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                {formatCurrency(price)}
              </span>
              <span className={changePct >= 0 ? 'text-green-400' : 'text-red-400'}>
                {formatPct(changePct)}
              </span>
            </div>
          )}
        </div>

        {generating && (
          <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--text-muted)' }}>
            <div className="w-4 h-4 border-2 border-blue-400/40 border-t-blue-400 rounded-full animate-spin" />
            Analyzing…
          </div>
        )}

        <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-white/10">
          <X size={18} style={{ color: 'var(--text-secondary)' }} />
        </button>
      </div>

      {/* Content */}
      <div className="h-full overflow-y-auto pb-20 px-4 md:px-6 pt-5 space-y-6" style={{ maxHeight: 'calc(100vh - 60px)' }}>

        {/* Prediction Cards — 6 horizons */}
        <section>
          <h3 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>PREDICTIONS</h3>
          {predsLoading ? (
            <div className="text-sm" style={{ color: 'var(--text-muted)' }}>Generating predictions…</div>
          ) : (
            <div className="flex gap-3 overflow-x-auto pb-1">
              {HORIZONS.map(h => (
                <PredCard key={h} pred={predsByHorizon[h] || { horizon_days: h, direction: 'Neutral', confidence: 0, risk_score: 50 }} />
              ))}
            </div>
          )}
        </section>

        {/* AI Explanation */}
        <section>
          <h3 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>AI ANALYSIS</h3>
          <div
            className="rounded-xl border p-4"
            style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}
          >
            {explanation ? (
              <p className="text-sm leading-relaxed" style={{ color: 'var(--text-primary)' }}>{explanation}</p>
            ) : (
              <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-muted)' }}>
                <div className="w-4 h-4 border-2 border-blue-400/40 border-t-blue-400 rounded-full animate-spin flex-shrink-0" />
                Generating analyst narrative…
              </div>
            )}
          </div>
        </section>

        {/* Agent Analysis */}
        <section>
          <h3 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>
            AGENT ANALYSIS ({agentResults.length}/42)
          </h3>
          {agentsLoading ? (
            <div className="text-sm" style={{ color: 'var(--text-muted)' }}>Loading agent outputs…</div>
          ) : agentResults.length > 0 ? (
            <div
              className="rounded-xl border overflow-hidden"
              style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}
            >
              <div className="px-3 py-1.5 flex items-center gap-2 text-xs border-b" style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
                <span className="w-6">ID</span>
                <span className="flex-1">Agent</span>
                <span>Signal</span>
                <span className="w-10 text-right">Score</span>
              </div>
              <div className="px-3 max-h-64 overflow-y-auto">
                {agentResults.map(a => <AgentRow key={a.agent_id} agent={a} />)}
              </div>
            </div>
          ) : (
            <div className="text-sm" style={{ color: 'var(--text-muted)' }}>No agent data yet. Generate a prediction first.</div>
          )}
        </section>

        {/* Symbol Details */}
        {quote && (
          <section>
            <h3 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>MARKET DATA</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { label: 'Volume', value: quote.volume?.toLocaleString() || '—' },
                { label: 'Market Cap', value: quote.market_cap_str || quote.market_cap?.toLocaleString() || '—' },
                { label: '52W High', value: formatCurrency(quote.week52_high) },
                { label: '52W Low', value: formatCurrency(quote.week52_low) },
              ].map(({ label, value }) => (
                <div key={label} className="rounded-lg border p-3" style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}>
                  <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{label}</div>
                  <div className="text-sm font-semibold mt-0.5" style={{ color: 'var(--text-primary)' }}>{value}</div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
