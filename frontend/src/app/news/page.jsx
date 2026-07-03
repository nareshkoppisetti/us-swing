'use client';
/**
 * File: frontend/src/app/news/page.jsx
 * News Intelligence — live articles with AI sentiment, economic calendar.
 * Wired to Phase 5 backend: /api/v1/news/, /api/v1/news/sentiment/{symbol},
 *                           /api/v1/news/economic-calendar, /api/v1/news/fetch
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import {
  RefreshCw, Newspaper, ExternalLink, Clock,
  TrendingUp, TrendingDown, Minus, Calendar, AlertTriangle,
} from 'lucide-react';

// ── Sentiment helpers ─────────────────────────────────────────────────────────
const SENTIMENT_MAP = {
  bullish:  { icon: TrendingUp,   cls: 'text-green-400 bg-green-400/10 border-green-400/30',  label: 'Bullish' },
  bearish:  { icon: TrendingDown, cls: 'text-red-400 bg-red-400/10 border-red-400/30',        label: 'Bearish' },
  neutral:  { icon: Minus,        cls: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30', label: 'Neutral' },
  positive: { icon: TrendingUp,   cls: 'text-green-400 bg-green-400/10 border-green-400/30',  label: 'Bullish' },
  negative: { icon: TrendingDown, cls: 'text-red-400 bg-red-400/10 border-red-400/30',        label: 'Bearish' },
};

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

function sentimentInfo(article) {
  const raw = article.sentiment || article.sentiment_label || 'neutral';
  const score = article.sentiment_score;
  if (score != null) {
    if (score > 0.05) return SENTIMENT_MAP.bullish;
    if (score < -0.05) return SENTIMENT_MAP.bearish;
    return SENTIMENT_MAP.neutral;
  }
  return SENTIMENT_MAP[raw?.toLowerCase()] || SENTIMENT_MAP.neutral;
}

// ── Subcomponents ─────────────────────────────────────────────────────────────
function NewsCard({ article }) {
  const si = sentimentInfo(article);
  const Icon = si.icon;
  const title = article.headline || article.title || '';
  const score = article.sentiment_score;

  return (
    <div className="rounded-xl border p-4 hover:border-opacity-70 transition-all"
      style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            {(article.symbols || []).slice(0, 4).map(s => (
              <span key={s} className="font-mono text-xs font-bold px-1.5 py-0.5 rounded"
                style={{ background: 'var(--bg-secondary)', color: '#2A7A6F' }}>{s}</span>
            ))}
            <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border font-semibold ${si.cls}`}>
              <Icon size={10} />{si.label}
            </span>
            {score != null && (
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {score >= 0 ? '+' : ''}{score.toFixed(2)}
              </span>
            )}
          </div>
          <h3 className="text-sm font-semibold leading-snug mb-2 line-clamp-2"
            style={{ color: 'var(--text-primary)' }}>{title}</h3>
          <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--text-muted)' }}>
            <span className="flex items-center gap-1">
              <Clock size={10} />
              {timeAgo(article.published_at || article.created_at)}
            </span>
            {article.source && <span>{article.source}</span>}
          </div>
        </div>
        {article.url && (
          <a href={article.url} target="_blank" rel="noopener noreferrer"
            className="p-1.5 rounded-lg hover:bg-white/10 flex-shrink-0"
            style={{ color: 'var(--text-muted)' }}>
            <ExternalLink size={14} />
          </a>
        )}
      </div>
    </div>
  );
}

function SentimentBar({ label, score, articleCount }) {
  if (articleCount == null || articleCount === 0) return null;
  const composite = score ?? 0;
  const pct = Math.round((composite + 1) * 50); // -1..+1 → 0..100
  const color = composite > 0.05 ? '#22c55e' : composite < -0.05 ? '#ef4444' : '#eab308';
  return (
    <div className="rounded-xl border p-4" style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold" style={{ color: 'var(--text-muted)' }}>
          {label} SENTIMENT
        </span>
        <span className="text-xs font-bold" style={{ color }}>
          {composite >= 0 ? '+' : ''}{composite.toFixed(3)}
        </span>
      </div>
      <div className="h-2 rounded-full overflow-hidden relative" style={{ background: 'var(--border)' }}>
        <div className="absolute left-1/2 top-0 w-px h-full bg-gray-500 z-10" />
        <div className="h-full rounded-full transition-all"
          style={{ width: `${pct}%`, background: color, transformOrigin: 'center' }} />
      </div>
      <p className="text-xs mt-1.5" style={{ color: 'var(--text-muted)' }}>
        {articleCount} articles analyzed
      </p>
    </div>
  );
}

function CalendarEvent({ event }) {
  const impact = event.impact === 'high';
  return (
    <div className="flex items-center gap-3 py-2 border-b last:border-0"
      style={{ borderColor: 'var(--border)' }}>
      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${impact ? 'bg-red-400' : 'bg-yellow-400'}`} />
      <div className="flex-1 min-w-0">
        <p className="text-xs font-semibold truncate" style={{ color: 'var(--text-primary)' }}>
          {event.name}
        </p>
        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{event.date}</p>
      </div>
      <span className={`text-xs font-bold flex-shrink-0 ${
        event.days_until === 0 ? 'text-red-400' :
        event.days_until <= 3 ? 'text-orange-400' : 'text-yellow-400'
      }`}>
        {event.days_until === 0 ? 'TODAY' : `${event.days_until}d`}
      </span>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────
const SYMBOLS = ['', 'SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA', 'AMZN', 'META', 'MSFT', 'GOOGL', 'GLD'];
const FILTERS = ['all', 'bullish', 'bearish', 'neutral'];

export default function NewsPage() {
  const [articles, setArticles] = useState([]);
  const [sentiment, setSentiment] = useState(null);
  const [calendar, setCalendar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const [filter, setFilter] = useState('all');
  const [symbol, setSymbol] = useState('');
  const [error, setError] = useState(null);
  const mountedRef = useRef(true);

  useEffect(() => { return () => { mountedRef.current = false; }; }, []);

  const loadAll = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const params = { limit: 60, hours: 48 };
      if (symbol) params.symbol = symbol;
      if (filter !== 'all') params.sentiment = filter;

      const [newsRes, calRes] = await Promise.allSettled([
        api.getNews(params),
        api.getEconomicCalendar(),
      ]);

      if (!mountedRef.current) return;

      if (newsRes.status === 'fulfilled') setArticles(newsRes.value.data || []);
      if (calRes.status === 'fulfilled') setCalendar(calRes.value.data || []);

      // Load sentiment summary if symbol selected
      if (symbol) {
        try {
          const sentRes = await api.getNewsSentiment(symbol);
          if (mountedRef.current) setSentiment(sentRes.data);
        } catch {}
      }
    } catch (e) {
      if (mountedRef.current) setError(e.message);
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, [symbol, filter]);

  useEffect(() => { loadAll(); }, [loadAll]);

  const handleFetchFresh = async () => {
    setFetching(true);
    try {
      await api.fetchFreshNews();
      await loadAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setFetching(false);
    }
  };

  const upcomingHigh = calendar.filter(e => e.impact === 'high').slice(0, 5);
  const allEvents = calendar.slice(0, 8);

  return (
    <MainLayout>
      <div className="p-4 md:p-6 space-y-5">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: 'rgba(42,122,111,0.12)' }}>
              <Newspaper size={20} color="#2A7A6F" />
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
                News Intelligence
              </h1>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                VADER + TextBlob AI-scored financial news
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <select value={symbol} onChange={e => setSymbol(e.target.value)}
              className="text-sm rounded-xl border px-3 py-2 outline-none"
              style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              {SYMBOLS.map(s => <option key={s} value={s}>{s || 'All symbols'}</option>)}
            </select>
            <div className="flex rounded-xl overflow-hidden border" style={{ borderColor: 'var(--border)' }}>
              {FILTERS.map(f => (
                <button key={f} onClick={() => setFilter(f)}
                  className="px-3 py-2 text-xs font-semibold capitalize transition-colors"
                  style={{
                    background: filter === f ? '#2A7A6F' : 'var(--bg-card)',
                    color: filter === f ? '#fff' : 'var(--text-secondary)',
                  }}>{f}</button>
              ))}
            </div>
            <button onClick={loadAll} disabled={loading}
              className="p-2 rounded-xl border hover:bg-white/5 transition-colors"
              style={{ borderColor: 'var(--border)' }}>
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} style={{ color: 'var(--text-muted)' }} />
            </button>
            <button onClick={handleFetchFresh} disabled={fetching}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white disabled:opacity-50"
              style={{ background: '#2A7A6F' }}>
              <RefreshCw size={13} className={fetching ? 'animate-spin' : ''} />
              Fetch Latest
            </button>
          </div>
        </div>

        {error && (
          <div className="rounded-xl border border-red-500/30 p-4 text-sm text-red-400"
            style={{ background: 'rgba(239,68,68,0.05)' }}>{error}</div>
        )}

        {/* Sentiment bar if symbol selected */}
        {sentiment && symbol && (
          <SentimentBar
            label={symbol}
            score={sentiment.composite_score}
            articleCount={sentiment.article_count}
          />
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
          {/* News Feed — 3 cols */}
          <div className="lg:col-span-3">
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="rounded-xl border animate-pulse h-32"
                    style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }} />
                ))}
              </div>
            ) : articles.length === 0 ? (
              <div className="rounded-xl border p-16 text-center"
                style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
                <Newspaper size={48} className="mx-auto mb-4 opacity-30" />
                <p className="text-base font-semibold mb-2">No articles found</p>
                <p className="text-sm mb-5">
                  Click &ldquo;Fetch Latest&rdquo; to pull and score live financial news
                </p>
                <button onClick={handleFetchFresh} disabled={fetching}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white"
                  style={{ background: '#2A7A6F' }}>
                  <RefreshCw size={13} className={fetching ? 'animate-spin' : ''} />
                  Fetch News Now
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {articles.map((a, i) => <NewsCard key={a.id || i} article={a} />)}
              </div>
            )}
          </div>

          {/* Economic Calendar sidebar — 1 col */}
          <div className="space-y-4">
            {/* Upcoming high-impact alert */}
            {upcomingHigh.length > 0 && upcomingHigh[0].days_until <= 3 && (
              <div className="rounded-xl border p-4"
                style={{ background: 'rgba(239,68,68,0.06)', borderColor: 'rgba(239,68,68,0.3)' }}>
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle size={13} className="text-red-400" />
                  <span className="text-xs font-bold text-red-400">HIGH-IMPACT EVENT</span>
                </div>
                <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {upcomingHigh[0].name}
                </p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  {upcomingHigh[0].days_until === 0 ? 'TODAY' : `in ${upcomingHigh[0].days_until} day${upcomingHigh[0].days_until > 1 ? 's' : ''}`}
                </p>
              </div>
            )}

            {/* Economic calendar */}
            <div className="rounded-xl border p-4"
              style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}>
              <div className="flex items-center gap-2 mb-3">
                <Calendar size={14} style={{ color: '#2A7A6F' }} />
                <h2 className="text-xs font-bold uppercase tracking-wider"
                  style={{ color: 'var(--text-muted)' }}>Economic Calendar</h2>
              </div>
              {allEvents.length > 0 ? (
                <div>
                  {allEvents.map((ev, i) => <CalendarEvent key={i} event={ev} />)}
                </div>
              ) : (
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>No events in next 45 days</p>
              )}
              <div className="flex gap-3 mt-3 text-xs" style={{ color: 'var(--text-muted)' }}>
                <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-red-400" />High impact</span>
                <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-yellow-400" />Medium</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
