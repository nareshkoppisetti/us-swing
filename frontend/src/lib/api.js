/**
 * File: frontend/src/lib/api.js
 * Central API client — all backend calls go through here.
 * Exports:  default api  AND  named { api }  for backward compat.
 *
 * SPEC Section 16.1 — REST API Endpoint Inventory
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ── Cookie utilities ──────────────────────────────────────────────────────────
export function getCookie(name) {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

function setCookie(name, value, minutes) {
  if (typeof document === 'undefined') return;
  const d = new Date();
  d.setTime(d.getTime() + minutes * 60 * 1000);
  document.cookie = `${name}=${encodeURIComponent(value)};expires=${d.toUTCString()};path=/;SameSite=Lax`;
}

export function clearAuthCookies() {
  if (typeof document === 'undefined') return;
  ['usa-swing-token', 'usa-swing-role', 'usa-swing-refresh', 'usa-swing-username'].forEach(name => {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
  });
}

// ── Auth helpers ──────────────────────────────────────────────────────────────
export async function refreshToken() {
  const refresh = getCookie('usa-swing-refresh');
  if (!refresh) throw new Error('No refresh token');
  const res = await fetch(`${BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh }),
  });
  if (!res.ok) throw new Error('Refresh failed');
  const data = await res.json();
  const token = data.data?.access_token || data.access_token;
  if (token) setCookie('usa-swing-token', token, 15);
  return token;
}

export async function login(username, password) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data?.error?.message || data?.detail || 'Login failed');
  // /auth/login returns the token payload FLAT (no {success, data, meta} envelope
  // unlike most other endpoints) — handle both shapes defensively.
  const { access_token, refresh_token, user } = data.data ?? data;
  setCookie('usa-swing-token', access_token, 15);
  setCookie('usa-swing-role', user?.role || '', 15);
  setCookie('usa-swing-username', user?.username || '', 15);
  if (refresh_token) setCookie('usa-swing-refresh', refresh_token, 60 * 24 * 7);
  return data.data ?? data;
}

export async function logout() {
  const token = getCookie('usa-swing-token');
  if (token) {
    try {
      await fetch(`${BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
    } catch {}
  }
  clearAuthCookies();
}

// ── Core ApiClient ────────────────────────────────────────────────────────────
class ApiClient {
  _getToken() { return getCookie('usa-swing-token'); }

  _buildHeaders(extra = {}) {
    const token = this._getToken();
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...extra,
    };
  }

  /** Build URL from path + optional params object (axios-style config.params support) */
  _buildURL(path, config = {}) {
    // Support both /api/v1/... absolute paths and relative paths
    let fullPath = path;
    if (path.startsWith('/api/v1/')) {
      fullPath = path.replace('/api/v1', '');
    } else if (path.startsWith('/api/')) {
      // legacy paths like /api/alerts/list → /alerts/list
      fullPath = path.replace('/api', '');
    }
    const url = new URL(`${BASE_URL}${fullPath}`);
    if (config.params) {
      Object.entries(config.params).forEach(([k, v]) => {
        if (v !== undefined && v !== null) url.searchParams.set(k, v);
      });
    }
    return url.toString();
  }

  async _fetch(path, options = {}, config = {}) {
    const url = this._buildURL(path, config);
    const res = await fetch(url, {
      ...options,
      headers: this._buildHeaders(options.headers || {}),
    });

    if (res.status === 401) {
      try {
        await refreshToken();
        const retry = await fetch(url, {
          ...options,
          headers: this._buildHeaders(options.headers || {}),
        });
        const retryData = await retry.json();
        if (!retry.ok) throw new Error(retryData?.error?.message || `HTTP ${retry.status}`);
        return retryData;
      } catch {
        clearAuthCookies();
        if (typeof window !== 'undefined') window.location.href = '/login?reason=session_expired';
        throw new Error('Unauthorized');
      }
    }

    const data = await res.json();
    if (!res.ok) throw new Error(data?.error?.message || data?.detail || `HTTP ${res.status}`);
    return data;
  }

  // ── Axios-compatible convenience methods (for legacy page code) ─────────────
  async get(path, config = {}) { return this._fetch(path, {}, config); }
  async post(path, body, config = {}) {
    return this._fetch(path, { method: 'POST', body: JSON.stringify(body) }, config);
  }
  async put(path, body, config = {}) {
    return this._fetch(path, { method: 'PUT', body: JSON.stringify(body) }, config);
  }
  async patch(path, body, config = {}) {
    return this._fetch(path, { method: 'PATCH', body: JSON.stringify(body) }, config);
  }
  async delete(path, config = {}) {
    return this._fetch(path, { method: 'DELETE' }, config);
  }

  // ── Auth ────────────────────────────────────────────────────────────────────
  async getMe() { return this._fetch('/auth/me'); }

  // ── Market Data ─────────────────────────────────────────────────────────────
  async getOHLCV(symbol, { timeframe = 'daily', period = '1y' } = {}) {
    return this._fetch(`/market/ohlcv/${symbol}?timeframe=${timeframe}&period=${period}`);
  }
  async getQuote(symbol) { return this._fetch(`/market/quote/${symbol}`); }
  async getIndicators(symbol) { return this._fetch(`/market/indicators/${symbol}`); }
  async getMarketRegime() { return this._fetch('/market/regime'); }

  // ── Symbol Search ───────────────────────────────────────────────────────────
  async searchSymbols(query, limit = 10) {
    return this._fetch(`/symbols/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  }
  async getSymbol(ticker) { return this._fetch(`/symbols/${ticker}`); }

  // ── Agents ──────────────────────────────────────────────────────────────────
  async listAgents() { return this._fetch('/agents/'); }
  async getAgentOutput(agentId, symbol) { return this._fetch(`/agents/${agentId}/output/${symbol}`); }
  async getAgentResults(symbol) { return this._fetch(`/agents/results/${symbol}`); }
  async triggerAgent(agentId, symbol) {
    return this._fetch(`/agents/run/${agentId}`, { method: 'POST', body: JSON.stringify({ symbol }) });
  }
  async getSchedulerStatus() { return this._fetch('/agents/status'); }
  async runAgents(symbol, agentIds = []) {
    return this._fetch('/agents/run', { method: 'POST', body: JSON.stringify({ symbol, agent_ids: agentIds }) });
  }

  // ── Predictions ─────────────────────────────────────────────────────────────
  async getPredictions(params = {}) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v != null) q.set(k, v); });
    return this._fetch(`/predictions/?${q}`);
  }
  async getPrediction(symbol) { return this._fetch(`/predictions/${symbol}`); }
  async getPredictionHistory(symbol, limit = 20) {
    return this._fetch(`/predictions/${symbol}/history?limit=${limit}`);
  }
  async generatePrediction(symbol) {
    return this._fetch(`/predictions/generate?symbol=${symbol}`, { method: 'POST' });
  }
  async getSymbolPredictions(symbol) {
    // Returns all horizon predictions for a symbol from Agent 33
    return this._fetch(`/predictions/${symbol}`).then(d => {
      const preds = d?.data?.predictions || [];
      return { ...d, data: preds };
    });
  }
  async getSignal(symbol) { return this._fetch(`/signals/${symbol}`); }

  // ── Explanations ─────────────────────────────────────────────────────────────
  async getExplanation(predictionId) { return this._fetch(`/explanations/${predictionId}`); }
  async getLatestExplanation(symbol) { return this._fetch(`/explanations/symbol/${symbol}`); }
  async regenerateExplanation(predictionId) {
    return this._fetch(`/explanations/regenerate/${predictionId}`, { method: 'POST' });
  }
  async getExplanationHistory(symbol, page = 1, perPage = 20) {
    return this._fetch(`/explanations/history/${symbol}?page=${page}&per_page=${perPage}`);
  }

  // ── News ─────────────────────────────────────────────────────────────────────
  async getNews(params = {}) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v != null) q.set(k, v); });
    return this._fetch(`/news/?${q}`);
  }
  async getNewsSentiment(symbol) { return this._fetch(`/news/sentiment/${symbol}`); }
  async getEconomicCalendar() { return this._fetch('/news/economic-calendar'); }
  async fetchFreshNews() { return this._fetch('/news/fetch', { method: 'POST' }); }

  // ── Institutional ────────────────────────────────────────────────────────────
  async getEtfFlows(symbol = 'SPY') { return this._fetch(`/institutional/etf-flows?symbol=${symbol}`); }
  async getInsiderTransactions(symbol, days = 90) { return this._fetch(`/institutional/insider?symbol=${symbol}&days=${days}`); }
  async get13fHoldings(symbol, quarters = 4) { return this._fetch(`/institutional/13f?symbol=${symbol}&quarters=${quarters}`); }
  async getDarkPool(symbol, weeks = 4) { return this._fetch(`/institutional/dark-pool?symbol=${symbol}&weeks=${weeks}`); }

  // ── Options ──────────────────────────────────────────────────────────────────
  async getOptionsChain(symbol) { return this._fetch(`/options/chain?symbol=${symbol}`); }
  async getPutCallRatio(symbol) { return this._fetch(`/options/put-call-ratio?symbol=${symbol}`); }
  async getGEX(symbol) { return this._fetch(`/options/gamma-exposure?symbol=${symbol}`); }
  async getMaxPain(symbol, expiry) { return this._fetch(`/options/max-pain?symbol=${symbol}&expiry=${expiry}`); }
  async getVIX() { return this._fetch('/options/vix-structure'); }

  // ── Signals ──────────────────────────────────────────────────────────────────
  async getSignals(params = {}) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v != null) q.set(k, v); });
    return this._fetch(`/signals/?${q}`);
  }
  async getWatchlistSignals() { return this._fetch('/signals/watchlist'); }
  async getSignalHistory(symbol, limit = 30) {
    return this._fetch(`/signals/history/${symbol}?limit=${limit}`);
  }

  // ── Backtesting ──────────────────────────────────────────────────────────────
  async runBacktest(params) {
    return this._fetch('/backtesting/run', { method: 'POST', body: JSON.stringify(params) });
  }
  async getBacktest(id) { return this._fetch(`/backtesting/${id}`); }
  async getBacktestResults(id) { return this._fetch(`/backtesting/${id}/results`); }
  async getBacktestHistory(symbol) { return this._fetch(`/backtesting/?symbol=${symbol}`); }

  // ── Performance ──────────────────────────────────────────────────────────────
  async getAccuracy(params = {}) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v != null) q.set(k, v); });
    return this._fetch(`/performance/accuracy?${q}`);
  }
  async getCalibration() { return this._fetch('/performance/calibration'); }
  async getResolvedHistory(params = {}) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v != null) q.set(k, v); });
    return this._fetch(`/performance/history?${q}`);
  }
  async resolvePredictions() { return this._fetch('/performance/resolve', { method: 'POST' }); }
  async getAgentPerformance() {
    // No per-agent accuracy tracking exists (would require scoring each of the
    // 42 agents individually against outcomes) — this surfaces real agent
    // operational health (run status, error counts) instead of fabricating
    // accuracy numbers.
    return this._fetch('/monitoring/agents');
  }
  async getModelPerformance() {
    // No model-training metadata exists (that's ML-pipeline territory) — this
    // reshapes the real per-horizon accuracy breakdown into the same shape
    // the Model Monitoring page expects, rather than fabricating training dates.
    const res = await this._fetch('/performance/accuracy');
    const byHorizon = res?.data?.by_horizon || [];
    const models = byHorizon.map((stats) => ({
      horizon_days: stats.horizon_days,
      model_name: 'Ensemble (Agents 30-33)',
      accuracy: stats.win_rate ?? (stats.accuracy_pct || 0) / 100,
      last_trained: null,
      is_active: true,
    }));
    return { success: true, data: models, meta: res?.meta || {} };
  }

  // ── Alerts ───────────────────────────────────────────────────────────────────
  async getAlerts(params = {}) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v != null) q.set(k, v); });
    return this._fetch(`/alerts/?${q}`);
  }
  async createAlert(data) {
    return this._fetch('/alerts/', { method: 'POST', body: JSON.stringify(data) });
  }
  async acknowledgeAlert(id) {
    // No separate "acknowledge" concept in the backend — acknowledging
    // deactivates the alert so it won't keep re-triggering.
    return this._fetch(`/alerts/${id}`, { method: 'PATCH', body: JSON.stringify({ is_active: false }) });
  }
  async updateAlert(id, data) {
    return this._fetch(`/alerts/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
  }
  async deleteAlert(id) {
    return this._fetch(`/alerts/${id}`, { method: 'DELETE' });
  }

  // ── Admin & Monitoring ───────────────────────────────────────────────────────
  async getSystemMetrics() { return this._fetch('/monitoring/metrics'); }
  async getAgentStatus() { return this._fetch('/monitoring/agents'); }
  async getDataSources() { return this._fetch('/monitoring/data-sources'); }
  async getApiHealth() { return this._fetch('/monitoring/api-keys'); }
  async getHealthDashboard() { return this._fetch('/monitoring/health'); }
  async getLogs(params = {}) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v != null) q.set(k, v); });
    return this._fetch(`/admin/logs?${q}`);
  }
  async getUsers() { return this._fetch('/admin/users'); }
  async createUser(data) { return this._fetch('/admin/users', { method: 'POST', body: JSON.stringify(data) }); }
  async updateUser(id, data) { return this._fetch(`/admin/users/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deleteUser(id) { return this._fetch(`/admin/users/${id}`, { method: 'DELETE' }); }
  async getSystemConfig() { return this._fetch('/admin/settings'); }
  async updateSystemConfig(data) { return this._fetch('/admin/settings', { method: 'PATCH', body: JSON.stringify(data) }); }
  async getSchedulerJobs() { return this._fetch('/admin/scheduler/jobs'); }
  async triggerSchedulerJob(jobId) { return this._fetch(`/admin/scheduler/${jobId}/trigger`, { method: 'POST' }); }
}

// Singleton — exported both as default AND named { api } for backward compat
export const api = new ApiClient();
export default api;