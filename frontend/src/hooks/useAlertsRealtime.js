import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'

export function useAlerts() {
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    let pusherClient = null
    const initPusher = async () => {
      try {
        const Pusher = (await import('pusher-js')).default
        const key = process.env.NEXT_PUBLIC_PUSHER_KEY
        if (!key) return
        pusherClient = new Pusher(key, { cluster: process.env.NEXT_PUBLIC_PUSHER_CLUSTER || 'us2' })
        const channel = pusherClient.subscribe('motm-alerts')
        channel.bind('new-alert', (data) => {
          setAlerts(prev => [data, ...prev].slice(0, 50))
          toast.custom(() => (
            <div className="card px-4 py-3 max-w-sm">
              <p className="text-xs font-semibold">🚨 Alert: {data.symbol} · {data.timeframe}</p>
              <p className="text-xs">{data.message?.substring(0, 80)}</p>
            </div>
          ), { duration: 5000 })
        })
      } catch (e) {
        console.warn('Pusher not initialized:', e.message)
      }
    }
    initPusher()
    return () => { pusherClient?.disconnect() }
  }, [])

  return alerts
}
