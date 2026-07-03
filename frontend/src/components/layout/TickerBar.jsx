/**
 * File: frontend/src/components/layout/TickerBar.jsx
 * Live scrolling ticker bar for major market symbols.
 *
 * SPEC Section 7.3, BUILD_PLAN Phase 18
 */
'use client';
import { useState, useEffect, useRef } from 'react';
import api from '@/lib/api';
import { useWebSocket } from '@/hooks/useWebSocket';

// symbol = ticker used to query the backend quote endpoint
// label  = human-readable name shown in the UI (no raw "^GSPC"-style tickers)
const TICKERS = [
  // Major US indices
  { symbol: '^GSPC', label: 'S&P 500' },
  { symbol: '^DJI', label: 'Dow Jones' },
  { symbol: '^IXIC', label: 'Nasdaq' },
  { symbol: '^RUT', label: 'Russell 2000' },
  // Tracking ETFs
  { symbol: 'SPY', label: 'SPY' },
  { symbol: 'QQQ', label: 'QQQ' },
  { symbol: 'DIA', label: 'DIA' },
  { symbol: 'IWM', label: 'IWM' },
  // Vol / commodities / rates
  { symbol: '^VIX', label: 'VIX' },
  { symbol: 'GLD', label: 'Gold' },
  { symbol: 'USO', label: 'Oil' },
  { symbol: 'TLT', label: '20Y Treasury' },
];

function TickerItem({ label, price, change, changePct }) {
  const up = change >= 0;
  return (
    <span className="inline-flex items-center gap-1.5 mx-4 whitespace-nowrap text-xs">
      <span className="font-bold" style={{ color: 'var(--text-primary)' }}>{label}</span>
      {price != null && (
        <>
          <span style={{ color: 'var(--text-secondary)' }}>${Number(price).toFixed(2)}</span>
          <span className={up ? 'text-green-400' : 'text-red-400'}>
            {up ? '+' : ''}{Number(changePct ?? 0).toFixed(2)}%
          </span>
        </>
      )}
      {price == null && <span style={{ color: 'var(--text-muted)' }}>—</span>}
    </span>
  );
}

// As fast as we can safely poll the quote endpoint. Note: today the
// backend doesn't yet push a live "market_data" tick over the websocket —
// this component still listens for one (see subscribe() below) so that
// the moment that feed exists, prices switch to instant push automatically
// with no frontend change required. Until then, this 1s poll is the fastest
// practical "no perceptible delay" update rate a browser can sustain —
// true microsecond-level updates aren't something any polling client (or
// realistically any UI, given screens repaint far slower than that) can do.
const FALLBACK_POLL_MS = 2000;

export default function TickerBar() {
  const [quotes, setQuotes] = useState({});
  const intervalRef = useRef(null);
  const { subscribe } = useWebSocket();

  const fetchQuotes = async () => {
    const results = await Promise.allSettled(
      TICKERS.map(t => api.getQuote(t.symbol).then(d => ({ symbol: t.symbol, ...(d.data || {}) })))
    );
    setQuotes(prevQuotes => {
      const newQ = { ...prevQuotes };
      results.forEach((r, i) => {
        const key = TICKERS[i].symbol;
        // Only replace a ticker's data if this poll actually returned a
        // price — a fulfilled-but-empty/partial response (rate limit,
        // transient hiccup) must not blank out the last good value.
        if (r.status === 'fulfilled' && r.value?.price != null) {
          newQ[key] = { ...newQ[key], ...r.value };
        }
      });
      return newQ;
    });
  };

  // Live push: every tick the server sends on the 'market_data' channel is
  // applied the instant it arrives — no waiting on a timer.
  useEffect(() => {
    const unsub = subscribe('market_data', (data) => {
      if (!data?.symbol) return;
      setQuotes(q => ({ ...q, [data.symbol]: { ...q[data.symbol], ...data } }));
    });
    return unsub;
  }, [subscribe]);

  useEffect(() => {
    fetchQuotes();
    intervalRef.current = setInterval(fetchQuotes, FALLBACK_POLL_MS);
    return () => clearInterval(intervalRef.current);
  }, []);

  return (
    <div
      className="h-8 border-b overflow-hidden flex items-center flex-shrink-0"
      style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}
    >
      <div className="flex items-center animate-marquee">
        {TICKERS.map(t => (
          <TickerItem
            key={t.symbol}
            label={t.label}
            price={quotes[t.symbol]?.price}
            change={quotes[t.symbol]?.change}
            changePct={quotes[t.symbol]?.change_pct}
          />
        ))}
        {/* Duplicate for seamless loop */}
        {TICKERS.map(t => (
          <TickerItem
            key={`${t.symbol}-2`}
            label={t.label}
            price={quotes[t.symbol]?.price}
            change={quotes[t.symbol]?.change}
            changePct={quotes[t.symbol]?.change_pct}
          />
        ))}
      </div>
    </div>
  );
}
