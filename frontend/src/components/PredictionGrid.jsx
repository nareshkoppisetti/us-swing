'use client'
import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { TrendingUp, TrendingDown, Minus, RefreshCw, Brain, ChevronDown, ChevronUp } from 'lucide-react'
import toast from 'react-hot-toast'
import { PREDICTION_HORIZONS } from '@/constants/markets'

// Spec FR-002 / Section 7.4: 6 prediction horizons — 2D, 5D, 10D, 20D, 30D, 60D
const HORIZONS = PREDICTION_HORIZONS.map(d => ({ key: d, label: `${d}D` }))

// ── Reasoning panel inside each card (Section 14 — Explainability Engine) ────
function ReasoningPanel({ predictionId, sharedReason }) {
  const [open, setOpen] = useState(false)
  const [reasoning, setReasoning] = useState(null)
  const [loading, setLoading] = useState(false)

  const toggle = async () => {
    if (open) { setOpen(false); return }
    if (sharedReason) {
      setReasoning(sharedReason)
      setOpen(true)
      return
    }

    if (!predictionId) { setOpen(true); return }
    setLoading(true)
    try {
      const res = await api.get(`/api/explanations/${predictionId}`)
      setReasoning(res.data?.narrative_text || 'No analyst narrative available for this prediction yet.')
      setOpen(true)
    } catch {
      setReasoning('No analyst narrative available for this prediction yet.')
      setOpen(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mt-4">
      <button
        onClick={toggle}
        className="w-full flex items-center justify-between gap-2 px-4 py-3 rounded-xl font-semibold transition-all"
        style={{
          background: open ? 'rgba(46,125,50,0.08)' : 'var(--bg-secondary)',
          color: open ? '#2A7A6F' : 'var(--text-secondary)',
          border: `1px solid ${open ? 'rgba(46,125,50,0.3)' : 'var(--border)'}`,
          fontSize: '14px',
        }}
      >
        <div className="flex items-center gap-2">
          {loading
            ? <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            : <Brain size={15} />
          }
          <span>Why This Move? (AI Explanation)</span>
        </div>
        {open ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
      </button>

      {open && (
        <div className="mt-3 p-4 rounded-xl animate-fade-in"
          style={{
            background: 'linear-gradient(135deg, rgba(46,125,50,0.04), rgba(25,118,210,0.04))',
            border: '1px solid var(--border)',
          }}>
          <div className="flex items-center gap-2 mb-3">
            <Brain size={15} style={{ color: '#2A7A6F' }} />
            <span className="font-bold text-sm" style={{ color: '#2A7A6F' }}>Analyst Narrative</span>
          </div>
          <p className="leading-relaxed" style={{ color: 'var(--text-primary)', fontSize: '14px' }}>
            {reasoning || 'Click Generate to run the agent pipeline and produce an explanation for this prediction.'}
          </p>
        </div>
      )}
    </div>
  )
}

// ── Single horizon card — FULL WIDTH (Spec FR-002: Direction, Confidence, Risk, Expected Move) ──
function PredictionCard({ horizon, data, loading, sharedReason }) {
  if (loading) return (
    <div className="card p-6 w-full flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="skeleton h-6 w-24" />
        <div className="skeleton h-8 w-28 rounded-full" />
      </div>
      <div className="skeleton h-10 w-36" />
      <div className="skeleton h-3 w-full rounded-full" />
      <div className="skeleton h-12 w-full rounded-xl" />
    </div>
  )

  const direction      = (data?.direction || 'Neutral')
  const directionKey   = direction.toLowerCase()
  const confidence     = data?.confidence ?? 0
  const riskScore      = data?.risk_score ?? 0
  const expectedMove   = data?.expected_move_pct ?? 0

  const dirCfg = {
    bullish: { icon: TrendingUp,   color: 'var(--bull-fg)',    badgeClass: 'badge-bull',    label: 'Bullish' },
    bearish: { icon: TrendingDown, color: 'var(--bear-fg)',    badgeClass: 'badge-bear',    label: 'Bearish' },
    neutral: { icon: Minus,        color: 'var(--neutral-fg)', badgeClass: 'badge-neutral', label: 'Neutral' },
  }
  const cfg  = dirCfg[directionKey] || dirCfg.neutral
  const Icon = cfg.icon

  return (
    <div className="card p-6 w-full flex flex-col gap-3 hover:shadow-lg transition-all">
      {/* Row 1 — horizon label + direction badge */}
      <div className="flex items-center justify-between">
        <span className="font-bold text-lg" style={{ color: 'var(--text-primary)' }}>
          {horizon.label} Horizon
        </span>
        <span className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full font-bold text-sm ${cfg.badgeClass}`}>
          <Icon size={14} />
          {cfg.label}
        </span>
      </div>

      {/* Row 2 — expected move + risk score */}
      <div className="flex items-end gap-6">
        <div>
          <div className="text-sm mb-0.5" style={{ color: 'var(--text-muted)' }}>Expected Move</div>
          <div className="num font-black" style={{ color: cfg.color, fontSize: '2.4rem', lineHeight: 1 }}>
            {expectedMove > 0 ? '+' : ''}{expectedMove.toFixed(2)}%
          </div>
        </div>
        <div className="mb-1 text-base">
          <div className="text-sm mb-0.5" style={{ color: 'var(--text-muted)' }}>Risk Score</div>
          <span className="num font-bold" style={{ color: riskScore >= 70 ? '#B5451B' : riskScore >= 40 ? '#C4873A' : '#2A7A6F' }}>
            {riskScore.toFixed(0)} / 100
          </span>
        </div>
      </div>

      {/* Row 3 — confidence bar */}
      <div>
        <div className="flex justify-between text-sm mb-1.5">
          <span style={{ color: 'var(--text-muted)' }}>Confidence</span>
          <span className="num font-bold"
            style={{ color: confidence >= 70 ? '#2A7A6F' : confidence >= 50 ? '#C4873A' : '#B5451B' }}>
            {confidence.toFixed(0)}%
          </span>
        </div>
        <div className="w-full h-2.5 rounded-full" style={{ background: 'var(--border)' }}>
          <div className="h-2.5 rounded-full transition-all"
            style={{
              width: `${confidence}%`,
              background: confidence >= 70 ? '#2A7A6F' : confidence >= 50 ? '#C4873A' : '#B5451B',
            }} />
        </div>
      </div>

      {/* Row 4 — Prediction ID + timestamp (Spec FR-002) */}
      {data?.id && (
        <div className="flex justify-between text-xs" style={{ color: 'var(--text-muted)' }}>
          <span className="num">ID: {data.id}</span>
          {data?.created_at && <span>{new Date(data.created_at).toLocaleString()}</span>}
        </div>
      )}

      {/* Row 5 — Explanation toggle */}
      <ReasoningPanel
        predictionId={data?.id}
        sharedReason={sharedReason}
      />
    </div>
  )
}

// ── Main grid — 6 prediction horizons (2D/5D/10D/20D/30D/60D) ─────────────────
export default function PredictionGrid({ symbol, loading: parentLoading }) {
  const [predictions,  setPredictions]  = useState({})
  const [loading,      setLoading]      = useState(true)
  const [generating,   setGenerating]   = useState(false)
  const [sharedReason, setSharedReason] = useState(null)

  const loadPredictions = async (sym) => {
    if (!sym) return
    setLoading(true)
    try {
      const res  = await api.get(`/api/predictions/symbol/${sym}`)
      const list = res.data?.predictions || res.data?.data || []
      const map  = {}
      list.forEach(p => { map[p.horizon_days] = p })
      setPredictions(map)
      setSharedReason(list[0]?.narrative_text || null)
    } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => {
    loadPredictions(symbol)
  }, [symbol])

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const res  = await api.post('/api/predictions/generate', { symbol })
      const list = res.data?.predictions || res.data?.data || []
      const map  = {}
      list.forEach(p => { map[p.horizon_days] = p })
      setPredictions(map)
      setSharedReason(res.data?.narrative_text || null)
      toast.success(`Analysis complete for ${symbol}!`)
    } catch {
      toast.error('Failed to generate predictions')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="card w-full flex flex-col">

      {/* Header */}
      <div className="flex items-center justify-between px-6 py-5 border-b" style={{ borderColor: 'var(--border)' }}>
        <div>
          <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
            Prediction Engine
          </h2>
          <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
            42-agent ensemble synthesis for&nbsp;
            <span className="num font-bold" style={{ color: '#2A7A6F' }}>{symbol}</span>
          </p>
        </div>

      </div>

      {/* Shared AI reasoning banner */}
      {sharedReason && (
        <div className="mx-6 mt-5 p-5 rounded-2xl animate-fade-in"
          style={{
            background: 'linear-gradient(135deg, rgba(46,125,50,0.06), rgba(25,118,210,0.06))',
            border: '1px solid rgba(46,125,50,0.2)',
          }}>
          <div className="flex items-center gap-2 mb-2">
            <Brain size={17} style={{ color: '#2A7A6F' }} />
            <span className="font-bold" style={{ color: '#2A7A6F', fontSize: '15px' }}>AI Market Analysis</span>
          </div>
          <p className="leading-relaxed" style={{ color: 'var(--text-primary)', fontSize: '15px' }}>
            {sharedReason}
          </p>
        </div>
      )}

      {/* Cards — single column, full width, one per horizon */}
      <div className="p-6 flex flex-col gap-4">
        {HORIZONS.map(horizon => (
          <PredictionCard
            key={horizon.key}
            horizon={horizon}
            data={predictions[horizon.key]}
            loading={loading || parentLoading}
            sharedReason={sharedReason}
          />
        ))}
      </div>
    </div>
  )
}
