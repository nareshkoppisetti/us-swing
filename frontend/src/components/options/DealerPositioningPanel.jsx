/**
 * File path: frontend/src/components/options/DealerPositioningPanel.jsx
 * Purpose: Dealer net positioning summary from GEX analysis. Shows whether dealers are long or short gamma at current spot.
 * Props: positioning, spotPrice, gammaFlip
 * TODO: Implement component UI and wire to API.
 */
'use client';
import React from 'react';
export default function DealerPositioningPanel({ positioning, spotPrice, gammaFlip }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <p className="text-muted-foreground text-sm">DealerPositioningPanel — not yet implemented</p>
    </div>
  );
}
