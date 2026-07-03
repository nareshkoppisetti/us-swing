'use client'
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Zap } from 'lucide-react'

const REGIMES = {
  bull: { label: 'Bull Market', icon: TrendingUp, class: 'badge-bull' },
  bear: { label: 'Bear Market', icon: TrendingDown, class: 'badge-bear' },
  neutral: { label: 'Neutral', icon: Minus, class: 'badge-neutral' },
  crisis: { label: 'Crisis Mode', icon: AlertTriangle, class: 'badge-bear' },
  recovery: { label: 'Recovery', icon: Zap, class: 'badge-bull' },
}

export default function RegimeBadge({ regime }) {
  // Support both old format (regime.regime) and new format (string)
  const regimeKey = typeof regime === 'string' ? regime : regime?.regime || 'neutral'
  const confidence = typeof regime === 'object' ? regime?.confidence : undefined
  const config = REGIMES[regimeKey] || REGIMES.neutral
  const Icon = config.icon
  return (
    <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold ${config.class}`}>
      <span className="live-dot" style={{ width: 6, height: 6 }} />
      <Icon size={11} />
      {config.label}
      {confidence && <span style={{ opacity: 0.85 }}>· {confidence}%</span>}
    </div>
  )
}
