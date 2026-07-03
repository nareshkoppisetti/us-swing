'use client'
import { Bell, BellOff, TrendingUp, TrendingDown, Zap, Clock, CheckCircle } from 'lucide-react'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'

function AlertCard({ alert, onDismiss }) {
  const isHigh = alert.accuracy_score >= 80
  const direction = alert.direction || 'neutral'

  return (
    <div className={`card p-4 border-l-4 ${direction === 'bull' ? 'border-l-green-500' : direction === 'bear' ? 'border-l-red-500' : 'border-l-gray-400'}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1.5">
            <span className="num font-bold" style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>{alert.symbol}</span>
            <span className="num font-medium px-1.5 py-0.5 rounded" style={{ background: 'var(--bg-secondary)', color: 'var(--text-secondary)', fontSize: '0.82rem' }}>
              {alert.timeframe}
            </span>
            <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-semibold ${direction === 'bull' ? 'badge-bull' : direction === 'bear' ? 'badge-bear' : 'badge-neutral'}`}
              style={{ fontSize: '0.82rem' }}>
              {direction === 'bull' ? <TrendingUp size={10} /> : direction === 'bear' ? <TrendingDown size={10} /> : null}
              {direction}
            </span>
            {isHigh && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-semibold badge-high-conf" style={{ fontSize: '0.78rem' }}>
                <Zap size={9} />HIGH CONF
              </span>
            )}
          </div>
          <p className="leading-relaxed" style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
            {alert.message || alert.before_reason?.substring(0, 120)}...
          </p>
          <div className="flex items-center gap-3 mt-2">
            <span className="num font-bold" style={{ color: alert.accuracy_score >= 70 ? 'var(--bull-fg)' : '#C4873A', fontSize: '0.85rem' }}>
              {alert.accuracy_score?.toFixed(0)}% accuracy
            </span>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
              <Clock size={10} className="inline mr-0.5" />
              {alert.created_at ? new Date(alert.created_at).toLocaleTimeString() : '--'}
            </span>
          </div>
        </div>
        <button onClick={() => onDismiss(alert.id)}
          className="shrink-0 p-1.5 rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-800"
          style={{ color: 'var(--text-secondary)' }}>
          <CheckCircle size={17} />
        </button>
      </div>
    </div>
  )
}

export default function AlertManager({ alerts, loading, onRefresh }) {
  const handleDismiss = async (alertId) => {
    try {
      await api.patch(`/api/alerts/${alertId}/dismiss`)
      toast.success('Alert dismissed')
      onRefresh?.()
    } catch { toast.error('Failed to dismiss') }
  }

  if (loading) return (
    <div className="flex flex-col gap-3">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="card p-4"><div className="skeleton h-20" /></div>
      ))}
    </div>
  )

  if (alerts.length === 0) return (
    <div className="text-center py-16" style={{ color: 'var(--text-muted)' }}>
      <BellOff size={42} className="mx-auto mb-3" style={{ opacity: 0.4 }} />
      <p className="text-sm">No alerts at this time</p>
      <p style={{ marginTop: 4, fontSize: '0.85rem' }}>Alerts fire when accuracy ≥ {process.env.NEXT_PUBLIC_ALERT_THRESHOLD || 70}%</p>
    </div>
  )

  return (
    <div className="flex flex-col gap-3">
      {alerts.map((alert, i) => (
        <AlertCard key={alert.id || i} alert={alert} onDismiss={handleDismiss} />
      ))}
    </div>
  )
}
