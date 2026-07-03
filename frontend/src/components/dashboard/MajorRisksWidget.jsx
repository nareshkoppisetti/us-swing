'use client';
/**
 * Wired to Agent 9 (Event Detection) actual output:
 *   supporting_data: { event_risk_score, next_event_name, days_ahead }
 * and Agent 24 (Uncertainty):
 *   supporting_data: { vix, vix_regime, term_structure }
 *   score = uncertainty_score
 */
export default function MajorRisksWidget({ risks, uncertaintyScore, eventRiskData }) {
  const riskItems       = risks || [];
  const score           = uncertaintyScore ?? 0;
  const nextEvent       = eventRiskData?.next_event_name;
  const daysAhead       = eventRiskData?.days_ahead;
  const eventRiskScore  = eventRiskData?.event_risk_score;

  const dynamicRisks = [];
  if (nextEvent) dynamicRisks.push(`${nextEvent}${daysAhead != null ? ` in ${daysAhead}d` : ''}`);
  if (score > 60) dynamicRisks.push(`Elevated uncertainty (score ${score.toFixed(0)}/100)`);
  if (eventRiskScore != null && eventRiskScore >= 3) dynamicRisks.push(`Event risk level: ${eventRiskScore}/5`);

  const allRisks = riskItems.length > 0
    ? riskItems
    : dynamicRisks.length > 0
    ? dynamicRisks
    : null;

  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Major Risks</span>
        {score > 60 && <span className="text-xs text-orange-400 font-semibold">HIGH</span>}
      </div>
      {allRisks ? (
        <ul className="space-y-1.5">
          {allRisks.slice(0, 4).map((r, i) => (
            <li key={i} className="flex items-start gap-1.5 text-xs">
              <span className="text-orange-400 mt-0.5 flex-shrink-0">⚠</span>
              <span style={{ color: 'var(--text-secondary)' }}>
                {typeof r === 'string' ? r : r.message || r.name}
              </span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>No major risks identified</p>
      )}
    </div>
  );
}
