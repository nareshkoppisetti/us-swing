'use client'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'

export default function AccuracyPanel({ data, loading }) {
  if (loading) return <div className="card p-4"><div className="skeleton h-48" /></div>
  if (!data) return null

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {data.weekly_accuracy && (
        <div className="card p-4">
          <h3 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Weekly Accuracy Trend</h3>
          <ResponsiveContainer width="100%" height={150}>
            <LineChart data={data.weekly_accuracy}>
              <XAxis dataKey="week" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
              <Tooltip formatter={v => [`${v.toFixed(1)}%`, 'Accuracy']} />
              <Line type="monotone" dataKey="accuracy" stroke="#2A7A6F" strokeWidth={2} dot={{ r: 3, fill: '#2A7A6F' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
      {data.by_direction && (
        <div className="card p-4">
          <h3 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Accuracy by Direction</h3>
          <ResponsiveContainer width="100%" height={150}>
            <BarChart data={data.by_direction}>
              <XAxis dataKey="direction" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
              <Tooltip formatter={v => [`${v.toFixed(1)}%`, 'Accuracy']} />
              <Bar dataKey="accuracy" fill="#2A7A6F" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
