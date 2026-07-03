'use client'
import { useState, useEffect } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import { useTheme } from '@/components/providers'
import { Settings, Sun, Moon, Bell, Volume2, RefreshCw, Shield, Cpu, Save } from 'lucide-react'
import toast from 'react-hot-toast'

const DEFAULT_SETTINGS = {
  refreshInterval: 30,
  alertThreshold: 70,
  soundEnabled: true,
  alertVolume: 'high',
  defaultSymbol: 'SPY',
  autoRefresh: true,
  showAgentDetails: true,
  notifyHighImpact: true,
}

export default function SettingsPage() {
  const { theme, toggleTheme } = useTheme()
  const [settings, setSettings] = useState(DEFAULT_SETTINGS)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('motm-settings')
    if (stored) setSettings({ ...DEFAULT_SETTINGS, ...JSON.parse(stored) })
  }, [])

  const handleSave = () => {
    localStorage.setItem('motm-settings', JSON.stringify(settings))
    setSaved(true)
    toast.success('Settings saved!')
    setTimeout(() => setSaved(false), 3000)
  }

  const Toggle = ({ value, onChange }) => (
    <button onClick={() => onChange(!value)}
      className={`w-11 h-6 rounded-full transition-colors relative ${value ? 'bg-[#2A7A6F]' : 'bg-gray-300 dark:bg-gray-600'}`}>
      <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ${value ? 'translate-x-5' : 'translate-x-0.5'}`} />
    </button>
  )

  return (
    <MainLayout>
      <div className="px-4 py-4 flex flex-col gap-6 max-w-2xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
              <Settings size={18} className="inline mr-2" />Settings
            </h1>
            <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>Customize your trading intelligence dashboard</p>
          </div>
          <button onClick={handleSave}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium text-white"
            style={{ background: '#2A7A6F' }}>
            <Save size={14} />{saved ? 'Saved!' : 'Save'}
          </button>
        </div>

        {/* Appearance */}
        <div className="card p-5 flex flex-col gap-4">
          <h2 className="text-sm font-semibold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <Sun size={15} />Appearance
          </h2>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm" style={{ color: 'var(--text-primary)' }}>Dark Mode</div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>Toggle between light and dark theme</div>
            </div>
            <Toggle value={theme === 'dark'} onChange={toggleTheme} />
          </div>
        </div>

        {/* Market Data */}
        <div className="card p-5 flex flex-col gap-4">
          <h2 className="text-sm font-semibold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <RefreshCw size={15} />Market Data
          </h2>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm" style={{ color: 'var(--text-primary)' }}>Auto-Refresh</div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>Automatically refresh market data</div>
            </div>
            <Toggle value={settings.autoRefresh} onChange={v => setSettings(s => ({ ...s, autoRefresh: v }))} />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm" style={{ color: 'var(--text-primary)' }}>Refresh Interval</div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>How often to fetch new data</div>
            </div>
            <select value={settings.refreshInterval}
              onChange={e => setSettings(s => ({ ...s, refreshInterval: parseInt(e.target.value) }))}
              className="px-3 py-1.5 rounded-lg border text-sm"
              style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              {[15, 30, 60, 120, 300].map(v => <option key={v} value={v}>{v}s</option>)}
            </select>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm" style={{ color: 'var(--text-primary)' }}>Default Index</div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>Primary index to show on dashboard</div>
            </div>
            <select value={settings.defaultSymbol}
              onChange={e => setSettings(s => ({ ...s, defaultSymbol: e.target.value }))}
              className="px-3 py-1.5 rounded-lg border text-sm num font-bold"
              style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
              {['SPY', 'QQQ', 'DIA', 'IWM'].map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>

        {/* Alerts */}
        <div className="card p-5 flex flex-col gap-4">
          <h2 className="text-sm font-semibold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <Bell size={15} />Alerts & Notifications
          </h2>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm" style={{ color: 'var(--text-primary)' }}>Alert Threshold</div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>Minimum accuracy score to trigger alerts</div>
            </div>
            <div className="flex items-center gap-2">
              <span className="num text-sm font-bold" style={{ color: '#2A7A6F' }}>{settings.alertThreshold}%</span>
              <input type="range" min={50} max={95} step={5} value={settings.alertThreshold}
                onChange={e => setSettings(s => ({ ...s, alertThreshold: parseInt(e.target.value) }))}
                className="w-24 accent-green-700" />
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm" style={{ color: 'var(--text-primary)' }}>Sound Notifications</div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>Play sound when alerts fire</div>
            </div>
            <Toggle value={settings.soundEnabled} onChange={v => setSettings(s => ({ ...s, soundEnabled: v }))} />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm" style={{ color: 'var(--text-primary)' }}>High-Impact Events</div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>Notify for Fed meetings, CPI reports</div>
            </div>
            <Toggle value={settings.notifyHighImpact} onChange={v => setSettings(s => ({ ...s, notifyHighImpact: v }))} />
          </div>
        </div>

        {/* AI / Agents */}
        <div className="card p-5 flex flex-col gap-4">
          <h2 className="text-sm font-semibold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <Cpu size={15} />AI Agents
          </h2>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm" style={{ color: 'var(--text-primary)' }}>Show Agent Details</div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>Show individual agent outputs on dashboard</div>
            </div>
            <Toggle value={settings.showAgentDetails} onChange={v => setSettings(s => ({ ...s, showAgentDetails: v }))} />
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
