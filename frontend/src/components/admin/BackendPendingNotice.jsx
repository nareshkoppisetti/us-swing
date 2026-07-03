/**
 * File: frontend/src/components/admin/BackendPendingNotice.jsx
 * Shown when an admin/monitoring endpoint returns NOT_IMPLEMENTED
 * (these backend modules are scheduled for a later build phase).
 */
'use client';
import { Construction } from 'lucide-react';

export default function BackendPendingNotice({ module = 'This module' }) {
  return (
    <div className="rounded-xl border p-10 text-center"
      style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
      <Construction size={40} className="mx-auto mb-4 opacity-40" />
      <p className="text-base font-semibold mb-1" style={{ color: 'var(--text-secondary)' }}>
        {module} backend pending
      </p>
      <p className="text-sm">This endpoint will be implemented in a future backend phase.</p>
    </div>
  );
}
