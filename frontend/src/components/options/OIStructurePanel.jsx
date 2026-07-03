/**
 * File path: frontend/src/components/options/OIStructurePanel.jsx
 * Purpose: Open interest heatmap by strike/expiry. Shows call wall, put wall, and max pain strike.
 * Props: oiData, symbol, maxPain
 * TODO: Implement component UI and wire to API.
 */
'use client';
import React from 'react';
export default function OIStructurePanel({ oiData, symbol, maxPain }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <p className="text-muted-foreground text-sm">OIStructurePanel — not yet implemented</p>
    </div>
  );
}
