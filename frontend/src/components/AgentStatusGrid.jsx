'use client'
import { TrendingUp, TrendingDown, Minus, Activity, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import { getAgentsByLayer, AGENT_LAYERS } from '@/lib/agents'

function AgentRow({ agent, data, loading }) {
  const [expanded, setExpanded] = useState(false)
  const Icon = agent.icon

  if (loading) return (
    <div className="flex items-center gap-3 py-3">
      <div className="skeleton w-10 h-10 rounded-xl" />
      <div className="flex-1">
        <div className="skeleton h-4 w-28 mb-2" />
        <div className="skeleton h-3 w-36" />
      </div>
      <div className="skeleton h-7 w-18 rounded-full" />
    </div>
  )

  const signal = data?.signal || 'N/A'
  const score = data?.score
  const explanation = data?.explanation

  const signalCfg = {
    bull:    { badgeClass: 'badge-bull',    iconColor: 'var(--bull-fg)',    boxClass: 'dir-box-bull',    icon: TrendingUp,   label: 'Bullish' },
    bear:    { badgeClass: 'badge-bear',    iconColor: 'var(--bear-fg)',    boxClass: 'dir-box-bear',    icon: TrendingDown, label: 'Bearish' },
    neutral: { badgeClass: 'badge-neutral', iconColor: 'var(--neutral-fg)', boxClass: 'dir-box-neutral', icon: Minus,        label: 'Neutral' },
    'N/A':   { badgeClass: 'badge-neutral', iconColor: 'var(--text-muted)', boxClass: 'dir-box-neutral', icon: Minus,        label: 'N/A' },
  }
  const cfg = signalCfg[signal] || signalCfg['N/A']
  const SigIcon = cfg.icon

  return (
    <div className="border-b last:border-b-0" style={{ borderColor: 'var(--border)' }}>
      <div
        className="flex items-center gap-3 py-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/30 rounded-xl px-2 transition-all"
        onClick={() => explanation && setExpanded(!expanded)}
      >
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${cfg.boxClass}`}>
          <Icon size={17} style={{ color: cfg.iconColor }} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-semibold" style={{ color: 'var(--text-primary)', fontSize: '0.92rem' }}>{agent.label}</div>
          <div className="truncate" style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>{agent.desc}</div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {score !== undefined && (
            <span className="num font-bold" style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>{Math.round(score)}</span>
          )}
          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full font-semibold ${cfg.badgeClass}`} style={{ fontSize: '0.82rem' }}>
            <SigIcon size={10} />
            {cfg.label}
          </span>
          {explanation && (
            <span style={{ color: 'var(--text-muted)' }}>
              {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </span>
          )}
        </div>
      </div>
      {expanded && explanation && (
        <div className="mx-2 mb-3 p-3 rounded-xl leading-relaxed animate-fade-in"
          style={{ background: 'var(--bg-secondary)', color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
          {explanation}
        </div>
      )}
    </div>
  )
}

function LayerSection({ layer, agents, agentData, loading, defaultExpanded = false }) {
  const [expanded, setExpanded] = useState(defaultExpanded)
  const layerAgentsData = agents.map(a => agentData[a.key])
  const bullCount = layerAgentsData.filter(d => d?.signal === 'bull').length
  const bearCount = layerAgentsData.filter(d => d?.signal === 'bear').length

  return (
    <div className="border rounded-xl overflow-hidden mb-2" style={{ borderColor: 'var(--border)' }}>
      <button
        onClick={() => setExpanded(e => !e)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-all"
        style={{ background: 'var(--bg-secondary)' }}
      >
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ background: layer.color }} />
          <span className="font-bold" style={{ color: 'var(--text-primary)', fontSize: '0.92rem' }}>{layer.label}</span>
          <span className="px-2 py-0.5 rounded-full" style={{ background: 'var(--border)', color: 'var(--text-secondary)', fontSize: '0.78rem' }}>
            {agents.length} agents
          </span>
        </div>
        <div className="flex items-center gap-3">
          {bullCount > 0 && <span className="badge-bull px-2.5 py-0.5 rounded-full font-bold" style={{ fontSize: '0.82rem' }}>{bullCount}↑</span>}
          {bearCount > 0 && <span className="badge-bear px-2.5 py-0.5 rounded-full font-bold" style={{ fontSize: '0.82rem' }}>{bearCount}↓</span>}
          {expanded ? <ChevronUp size={15} style={{ color: 'var(--text-secondary)' }} /> : <ChevronDown size={15} style={{ color: 'var(--text-secondary)' }} />}
        </div>
      </button>
      {expanded && (
        <div className="px-4 animate-fade-in divide-y" style={{ borderColor: 'var(--border)' }}>
          {agents.map(agent => (
            <AgentRow key={agent.key} agent={agent} data={agentData[agent.key]} loading={loading} />
          ))}
        </div>
      )}
    </div>
  )
}

export default function AgentStatusGrid({ summary, loading }) {
  const layerMap = getAgentsByLayer()
  const agentData = summary?.agents || {}

  const allAgents = Object.values(layerMap).flatMap(l => l.agents)
  const allBull = allAgents.filter(a => agentData[a.key]?.signal === 'bull').length
  const allBear = allAgents.filter(a => agentData[a.key]?.signal === 'bear').length
  const hasData = Object.keys(agentData).length > 0

  return (
    <div className="card flex flex-col w-full">
      <div className="flex items-center justify-between px-6 py-5 border-b" style={{ borderColor: 'var(--border)' }}>
        <div>
          <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>AI Agent Signals</h2>
          <p className="mt-0.5" style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
            42 agents across 8 categories
            {hasData ? ' — click layer to expand' : ' — generate predictions to activate'}
          </p>
        </div>
        {!loading && hasData && (
          <div className="flex items-center gap-2">
            <span className="badge-bull px-3 py-1 rounded-full font-bold" style={{ fontSize: '0.92rem' }}>{allBull} ↑</span>
            <span className="badge-bear px-3 py-1 rounded-full font-bold" style={{ fontSize: '0.92rem' }}>{allBear} ↓</span>
          </div>
        )}
      </div>

      <div className="px-4 py-3">
        {!hasData && !loading && (
          <div className="text-center py-10" style={{ color: 'var(--text-muted)' }}>
            <Activity size={38} className="mx-auto mb-3" style={{ opacity: 0.35 }} />
            <p style={{ fontSize: '0.95rem' }}>No agent data yet.</p>
            <p style={{ marginTop: 4, fontSize: '0.92rem' }}>Click <strong>Generate</strong> to run the 42-agent AI analysis.</p>
          </div>
        )}
        {AGENT_LAYERS.map((layer, i) => {
          const layerData = layerMap[layer.id]
          if (!layerData) return null
          return (
            <LayerSection
              key={layer.id}
              layer={layer}
              agents={layerData.agents}
              agentData={agentData}
              loading={loading}
              defaultExpanded={i === 0}
            />
          )
        })}
      </div>
    </div>
  )
}
