/**
 * File path: frontend/src/components/alerts/AlertCard.jsx
 * Purpose: Card for a single alert: symbol, type, threshold, active status, last triggered time, delete button.
 * Props: alert, onDelete, onToggle
 * TODO: Implement component UI and wire to API.
 */
'use client';
import React from 'react';
export default function AlertCard({ alert, onDelete, onToggle }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <p className="text-muted-foreground text-sm">AlertCard — not yet implemented</p>
    </div>
  );
}
