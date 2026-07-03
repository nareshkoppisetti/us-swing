'use client';
import { confidenceColor } from '@/lib/utils';

export default function ConfidenceScoreWidget({ confidence }) {
  const val = confidence ?? 0;
  const color = val >= 75 ? '#22c55e' : val >= 55 ? '#eab308' : '#ef4444';
  const circumference = 2 * Math.PI * 28;
  const offset = circumference * (1 - val / 100);

  return (
    <div className="rounded-xl border p-4 h-full" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Confidence</span>
      </div>
      <div className="flex items-center gap-4">
        <svg width="72" height="72" viewBox="0 0 72 72">
          <circle cx="36" cy="36" r="28" fill="none" stroke="currentColor" className="text-gray-700" strokeWidth="6" />
          <circle cx="36" cy="36" r="28" fill="none" stroke={color} strokeWidth="6"
            strokeDasharray={circumference} strokeDashoffset={offset}
            strokeLinecap="round" transform="rotate(-90 36 36)" />
          <text x="36" y="41" textAnchor="middle" fill={color} fontSize="16" fontWeight="700">{val.toFixed(0)}</text>
        </svg>
        <div>
          <div className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
            {val >= 75 ? 'High' : val >= 55 ? 'Moderate' : 'Low'}
          </div>
          <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Signal strength</div>
        </div>
      </div>
    </div>
  );
}
