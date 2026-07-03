'use client';
/**
 * File: frontend/src/app/agents/page.jsx
 * Agent status grid — shows all 42 agents, their last signal/score,
 * and lets the user trigger a full run for any symbol.
 */
import { useState, useCallback } from 'react';
import { useAgentDefinitions, useAgentResults, useRunAgents, useAgentsByCategory } from '@/hooks/useAgents';
import { useWebSocket } from '@/hooks/useWebSocket';
import MainLayout from '@/components/layout/MainLayout';

const SIGNAL_COLORS = {
  Bullish: 'text-green-400 bg-green-400/10 border-green-400/30',
  Bearish: 'text-red-400 bg-red-400/10 border-red-400/30',
  Neutral: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30',
};

const SIGNAL_DOTS = { Bullish: 'bg-green-400', Bearish: 'bg-red-400', Neutral: 'bg-yellow-400' };

function AgentCard({ agent, result }) {
  const signal = result?.signal || 'Neutral';
  const score = result?.score;
  const conf = result?.confidence;
  const hasError = !!result?.error;

  return (
    <div className={`rounded-lg border p-3 bg-gray-900 transition-all ${hasError ? 'border-gray-700 opacity-60' : 'border-gray-700 hover:border-gray-500'}`}>
      <div className="flex items-start justify-between gap-2 mb-1">
        <div className="flex items-center gap-1.5 min-w-0">
          <span className="text-xs text-gray-500 font-mono shrink-0">#{agent.agent_id}</span>
          <span className="text-sm text-gray-200 font-medium truncate">{agent.agent_name}</span>
        </div>
        {result && !hasError && (
          <span className={`text-xs px-1.5 py-0.5 rounded border font-medium shrink-0 ${SIGNAL_COLORS[signal] || SIGNAL_COLORS.Neutral}`}>
            {signal}
          </span>
        )}
        {hasError && <span className="text-xs text-red-400 shrink-0">ERR</span>}
      </div>

      {result && !hasError && (
        <div className="flex items-center gap-3 mt-1.5">
          <div className="flex-1">
            <div className="flex justify-between text-xs text-gray-500 mb-0.5">
              <span>Score</span><span>{score?.toFixed(1)}</span>
            </div>
            <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${signal === 'Bullish' ? 'bg-green-500' : signal === 'Bearish' ? 'bg-red-500' : 'bg-yellow-500'}`}
                style={{ width: `${Math.max(0, Math.min(100, score || 50))}%` }}
              />
            </div>
          </div>
          <span className="text-xs text-gray-400 shrink-0">{conf?.toFixed(0)}%</span>
        </div>
      )}

      {!result && (
        <div className="text-xs text-gray-600 mt-1">
          {agent.refresh_frequency} · {agent.dependencies?.length > 0 ? `deps: ${agent.dependencies.join(',')}` : 'independent'}
        </div>
      )}
    </div>
  );
}

export default function AgentsPage() {
  const [symbol, setSymbol] = useState('SPY');
  const [inputSymbol, setInputSymbol] = useState('SPY');
  const [liveResults, setLiveResults] = useState({});

  const { agents } = useAgentDefinitions();
  const { results, loading: resultsLoading, refetch } = useAgentResults(symbol);
  const { run, running, error: runError } = useRunAgents(symbol);

  // Merge DB results with live WS updates
  const mergedResults = {};
  for (const r of results) mergedResults[r.agent_id] = r;
  for (const [id, r] of Object.entries(liveResults)) mergedResults[id] = r;

  // WebSocket for live agent updates
  useWebSocket(symbol, {
    onAgentUpdate: useCallback((msg) => {
      setLiveResults(prev => ({ ...prev, [msg.agent_id]: msg }));
    }, []),
  });

  const byCategory = useAgentsByCategory(Object.values(mergedResults));

  const handleRun = async () => {
    setLiveResults({});
    await run();
    refetch();
  };

  const handleSymbolSubmit = (e) => {
    e.preventDefault();
    if (inputSymbol.trim()) {
      setSymbol(inputSymbol.trim().toUpperCase());
      setLiveResults({});
    }
  };

  // Summary counts
  const allResults = Object.values(mergedResults);
  const bullCount = allResults.filter(r => r.signal === 'Bullish').length;
  const bearCount = allResults.filter(r => r.signal === 'Bearish').length;
  const neutCount = allResults.filter(r => r.signal === 'Neutral').length;

  return (
    <MainLayout>
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white">Agent Pipeline</h1>
            <p className="text-gray-400 text-sm mt-0.5">42-agent signal analysis engine</p>
          </div>
          <form onSubmit={handleSymbolSubmit} className="flex items-center gap-2">
            <input
              className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 w-28 uppercase"
              value={inputSymbol}
              onChange={e => setInputSymbol(e.target.value.toUpperCase())}
              placeholder="SYMBOL"
            />
            <button
              type="submit"
              className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Set
            </button>
            <button
              type="button"
              onClick={handleRun}
              disabled={running}
              className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
            >
              {running ? (
                <><span className="animate-spin">⟳</span> Running...</>
              ) : '▶ Run All Agents'}
            </button>
          </form>
        </div>

        {/* Summary bar */}
        {allResults.length > 0 && (
          <div className="flex items-center gap-4 mb-6 p-4 bg-gray-900 rounded-xl border border-gray-800">
            <span className="text-gray-400 text-sm font-medium">{symbol}</span>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-400" />
              <span className="text-green-400 text-sm font-semibold">{bullCount} Bullish</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-red-400" />
              <span className="text-red-400 text-sm font-semibold">{bearCount} Bearish</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-yellow-400" />
              <span className="text-yellow-400 text-sm font-semibold">{neutCount} Neutral</span>
            </div>
            <span className="ml-auto text-gray-500 text-xs">{allResults.length} / 42 agents</span>
          </div>
        )}

        {runError && (
          <div className="mb-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">
            {runError}
          </div>
        )}

        {/* Category grids */}
        {Object.keys(byCategory).length > 0 ? (
          Object.entries(byCategory).map(([cat, catResults]) => {
            const catAgents = agents.filter(a => {
              if (cat === 'Direction') return a.agent_id <= 6;
              if (cat === 'News & Macro') return a.agent_id >= 7 && a.agent_id <= 14;
              if (cat === 'Institutional') return a.agent_id >= 15 && a.agent_id <= 20;
              if (cat === 'Strength') return a.agent_id >= 21 && a.agent_id <= 26;
              if (cat === 'Exit & Reversal') return a.agent_id >= 27 && a.agent_id <= 29;
              if (cat === 'Prediction Layer') return a.agent_id >= 30 && a.agent_id <= 33;
              if (cat === 'Additional') return a.agent_id === 34;
              if (cat === 'Commodity') return a.agent_id >= 35;
              return false;
            });
            const bullish = catResults.filter(r => r.signal === 'Bullish').length;
            const bearish = catResults.filter(r => r.signal === 'Bearish').length;

            return (
              <div key={cat} className="mb-6">
                <div className="flex items-center gap-3 mb-3">
                  <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">{cat}</h2>
                  <div className="flex-1 h-px bg-gray-800" />
                  {catResults.length > 0 && (
                    <span className="text-xs text-gray-500">
                      {bullish}🟢 {bearish}🔴
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-2">
                  {catAgents.map(agent => (
                    <AgentCard
                      key={agent.agent_id}
                      agent={agent}
                      result={mergedResults[agent.agent_id]}
                    />
                  ))}
                </div>
              </div>
            );
          })
        ) : agents.length > 0 ? (
          /* Show all agent definitions (no results yet) */
          Object.entries(
            agents.reduce((acc, a) => {
              let cat = 'Other';
              if (a.agent_id <= 6) cat = 'Direction';
              else if (a.agent_id <= 14) cat = 'News & Macro';
              else if (a.agent_id <= 20) cat = 'Institutional';
              else if (a.agent_id <= 26) cat = 'Strength';
              else if (a.agent_id <= 29) cat = 'Exit & Reversal';
              else if (a.agent_id <= 33) cat = 'Prediction Layer';
              else if (a.agent_id === 34) cat = 'Additional';
              else cat = 'Commodity';
              if (!acc[cat]) acc[cat] = [];
              acc[cat].push(a);
              return acc;
            }, {})
          ).map(([cat, catAgents]) => (
            <div key={cat} className="mb-6">
              <div className="flex items-center gap-3 mb-3">
                <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">{cat}</h2>
                <div className="flex-1 h-px bg-gray-800" />
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-2">
                {catAgents.map(a => (
                  <AgentCard key={a.agent_id} agent={a} result={null} />
                ))}
              </div>
            </div>
          ))
        ) : (
          <div className="text-center text-gray-500 py-20">
            {running ? 'Running agents…' : 'Enter a symbol and click Run All Agents'}
          </div>
        )}
      </div>
    </div>
    </MainLayout>
  );
}
