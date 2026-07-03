/**
 * File path: frontend/src/components/predictions/PredictionTable.jsx
 * Purpose: Sortable, filterable table of predictions. Columns: symbol, date, horizon, direction, confidence, risk, expiry, status.
 * Props: predictions, onRowClick, loading
 * TODO: Implement component UI and wire to API.
 */
'use client';
import React from 'react';
export default function PredictionTable({ predictions, onRowClick, loading }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <p className="text-muted-foreground text-sm">PredictionTable — not yet implemented</p>
    </div>
  );
}
