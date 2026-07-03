'use client';
import { Building2 } from 'lucide-react';
export default function InstitutionalFlowSummary({ flows }) {
  const net = flows?.net_flow ?? 0;
  const up = net >= 0;
  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Institutional Flows</span>
        <Building2 size={14} style={{ color: 'var(--text-muted)' }} />
      </div>
      <div className={`text-xl font-black ${up ? 'text-green-400' : 'text-red-400'}`}>
        {up ? '▲ Inflow' : '▼ Outflow'}
      </div>
      <div className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
        {flows?.summary || 'Net institutional capital flow tracking'}
      </div>
    </div>
  );
}
