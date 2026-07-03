'use client'
import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { api } from '@/lib/api'

const USA_SYMBOLS = [
  'SPY', 'QQQ', 'DIA', 'IWM',
  'AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'GOOGL', 'META', 'NFLX',
  'AMD', 'JPM', 'BAC', 'GS', 'V', 'UNH', 'XOM', 'BRK-B'
]


export default function TickerBar({ marketData = {} }) {
  const [extraData, setExtraData] = useState({})

  const DEFAULT_SYMBOLS = USA_SYMBOLS

  useEffect(() => {
    const missing = DEFAULT_SYMBOLS.filter(s => !marketData[s])
    if (missing.length === 0) return
    api.get(`/api/market/quotes?symbols=${missing.join(',')}`)
      .then(res => setExtraData(res.data || {}))
      .catch(() => {})
  }, [marketData])

  const allData = { ...extraData, ...marketData }
  const currencySymbol = '$'

  const tickers = DEFAULT_SYMBOLS.map(s => ({
    symbol: s,
    price: allData[s]?.price,
    change: allData[s]?.change_percent || 0,
  }))

  return (
    <div className="border-b overflow-hidden" style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)', height: '36px' }}>
      <div className="ticker-wrap h-full">
        <div className="ticker-inner h-full items-center" style={{ display: 'flex' }}>
          {[...tickers, ...tickers].map((t, i) => (
            <div key={i} className="flex items-center gap-2 px-5 shrink-0 h-full border-r" style={{ borderColor: 'var(--border)' }}>
              <span className="num text-xs font-bold" style={{ color: 'var(--text-primary)' }}>{t.symbol}</span>
              <span className="num text-xs" style={{ color: 'var(--text-secondary)' }}>
                {t.price ? `${currencySymbol}${typeof t.price === 'number' ? t.price.toFixed(2) : t.price}` : '--'}
              </span>
              <span className={`num text-xs flex items-center gap-0.5 ${t.change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {t.change >= 0 ? <TrendingUp size={9} /> : <TrendingDown size={9} />}
                {typeof t.change === 'number' ? `${t.change >= 0 ? '+' : ''}${t.change.toFixed(2)}%` : '--'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
