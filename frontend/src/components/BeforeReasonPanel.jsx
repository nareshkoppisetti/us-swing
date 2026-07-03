'use client'
import { useState } from 'react'
import { Brain, ChevronDown, ChevronUp, TrendingUp, TrendingDown, Minus, Clock } from 'lucide-react'

export default function BeforeReasonPanel({ prediction }) {
  const [expanded, setExpanded] = useState(false)
  const direction = prediction?.direction || 'neutral'
  const cfg = {
    bull:    { badgeClass: 'badge-bull',    boxClass: 'dir-box-bull',    iconColor: 'var(--bull-fg)',    icon: TrendingUp,   label: 'Bullish' },
    bear:    { badgeClass: 'badge-bear',    boxClass: 'dir-box-bear',    iconColor: 'var(--bear-fg)',    icon: TrendingDown, label: 'Bearish' },
    neutral: { badgeClass: 'badge-neutral', boxClass: 'dir-box-neutral', iconColor: 'var(--neutral-fg)', icon: Minus,        label: 'Neutral' },
  }[direction] || { badgeClass: 'badge-neutral', boxClass: 'dir-box-neutral', iconColor: 'var(--neutral-fg)', icon: Minus, label: 'Neutral' }
  const Icon = cfg.icon
  const changeColor = direction === 'bull' ? 'var(--bull-fg)' : direction === 'bear' ? 'var(--bear-fg)' : 'var(--text-secondary)'

  return (
    <div className="card overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${cfg.boxClass}`}>
          <Brain size={17} style={{ color: cfg.iconColor }} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold num" style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>
              {prediction.symbol} · {prediction.timeframe}
            </span>
            <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${cfg.badgeClass}`}>
              <Icon size={10} />{cfg.label}
            </span>
            <span className="num text-sm font-bold" style={{ color: changeColor }}>
              {prediction.predicted_change > 0 ? '+' : ''}{prediction.predicted_change?.toFixed(2)}%
            </span>
          </div>
          <div className="mt-0.5 truncate" style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            <Brain size={10} className="inline mr-1" />
            {prediction.before_reason?.substring(0, 100)}...
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <div className="text-right">
            <div className="num font-bold" style={{ color: prediction.accuracy_score >= 70 ? 'var(--bull-fg)' : '#C4873A', fontSize: '0.95rem' }}>
              {prediction.accuracy_score?.toFixed(0)}%
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>accuracy</div>
          </div>
          {expanded ? <ChevronUp size={15} style={{ color: 'var(--text-secondary)' }} /> : <ChevronDown size={15} style={{ color: 'var(--text-secondary)' }} />}
        </div>
      </button>

      {expanded && (
        <div className="border-t px-4 pb-4 pt-3" style={{ borderColor: 'var(--border)' }}>
          <div className="flex items-start gap-2 mb-3">
            <Brain size={15} className="mt-0.5 shrink-0" style={{ color: 'var(--brand-green)' }} />
            <div>
              <div className="font-semibold mb-1" style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>AI Reasoning (Before Prediction)</div>
              <p className="leading-relaxed" style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>
                {prediction.before_reason || 'No reasoning available'}
              </p>
            </div>
          </div>

          {prediction.agent_signals && (
            <div className="mt-3 pt-3 border-t" style={{ borderColor: 'var(--border)' }}>
              <div className="font-semibold mb-2" style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Agent Signals Used</div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5">
                {Object.entries(prediction.agent_signals).map(([agent, signal]) => (
                  <div key={agent} className="flex items-center gap-1.5 px-2 py-1.5 rounded-lg"
                    style={{ background: 'var(--bg-secondary)', fontSize: '0.82rem' }}>
                    <span className="font-medium capitalize" style={{ color: 'var(--text-secondary)' }}>{agent}</span>
                    <span className={`ml-auto px-1.5 rounded font-bold ${signal === 'bull' ? 'badge-bull' : signal === 'bear' ? 'badge-bear' : 'badge-neutral'}`}
                      style={{ fontSize: '0.75rem' }}>
                      {signal}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex items-center gap-2 mt-3" style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
            <Clock size={11} />
            Generated: {prediction.created_at ? new Date(prediction.created_at).toLocaleString() : '--'}
            {prediction.validate_at && ` · Validates: ${new Date(prediction.validate_at).toLocaleString()}`}
          </div>
        </div>
      )}
    </div>
  )
}
