/**
 * File path: frontend/src/components/admin/AgentStatusTable.jsx
 * Purpose: Table of all 42 agents with columns: ID, name, category, status badge, last run, duration, 24h errors, 30d accuracy.
 * Props: agents, loading, onTrigger
 * TODO: Implement component UI and wire to API.
 */
'use client';
import React from 'react';
export default function AgentStatusTable({ agents, loading, onTrigger }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <p className="text-muted-foreground text-sm">AgentStatusTable — not yet implemented</p>
    </div>
  );
}
