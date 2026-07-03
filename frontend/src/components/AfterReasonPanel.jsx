'use client'
import { useState } from 'react'
import { CheckCircle, XCircle, ChevronDown, ChevronUp, Clock } from 'lucide-react'

export default function AfterReasonPanel({ prediction }) {
  const [expanded, setExpanded] = useState(false)
  const isSuccess = prediction?.outcome === 'correct'

  return (
    <div className="card overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${isSuccess ? 'dir-box-bull' : 'dir-box-bear'}`}>
          {isSuccess
            ? <CheckCircle size={17} style={{ color: 'var(--bull-fg)' }} />
            : <XCircle    size={17} style={{ color: 'var(--bear-fg)' }} />}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-semibold num" style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>
              {prediction.symbol} · {prediction.timeframe}
            </span>
            <span className={`px-2.5 py-0.5 rounded-full font-semibold ${isSuccess ? 'badge-bull' : 'badge-bear'}`} style={{ fontSize: '0.82rem' }}>
              {isSuccess ? '✓ Correct' : '✗ Incorrect'}
            </span>
          </div>
          <div className="mt-0.5 truncate" style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Predicted: {prediction.direction} {prediction.predicted_change > 0 ? '+' : ''}{prediction.predicted_change?.toFixed(2)}%
            {prediction.actual_change !== undefined && ` · Actual: ${prediction.actual_change > 0 ? '+' : ''}${prediction.actual_change?.toFixed(2)}%`}
          </div>
        </div>
        {expanded ? <ChevronUp size={15} style={{ color: 'var(--text-secondary)' }} /> : <ChevronDown size={15} style={{ color: 'var(--text-secondary)' }} />}
      </button>

      {expanded && (
        <div className="border-t px-4 pb-4 pt-3" style={{ borderColor: 'var(--border)' }}>
          {isSuccess && prediction.after_success_reason && (
            <div className="flex items-start gap-2 mb-3">
              <CheckCircle size={15} className="mt-0.5 shrink-0" style={{ color: 'var(--bull-fg)' }} />
              <div>
                <div className="font-semibold mb-1" style={{ color: 'var(--bull-fg)', fontSize: '0.85rem' }}>Why It Succeeded</div>
                <p className="leading-relaxed" style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>{prediction.after_success_reason}</p>
              </div>
            </div>
          )}
          {!isSuccess && prediction.after_fail_reason && (
            <div className="flex items-start gap-2 mb-3">
              <XCircle size={15} className="mt-0.5 shrink-0" style={{ color: 'var(--bear-fg)' }} />
              <div>
                <div className="font-semibold mb-1" style={{ color: 'var(--bear-fg)', fontSize: '0.85rem' }}>Why It Failed</div>
                <p className="leading-relaxed" style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>{prediction.after_fail_reason}</p>
              </div>
            </div>
          )}
          <div className="flex items-center gap-2 mt-3" style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
            <Clock size={11} />
            Validated: {prediction.validated_at ? new Date(prediction.validated_at).toLocaleString() : '--'}
          </div>
        </div>
      )}
    </div>
  )
}
