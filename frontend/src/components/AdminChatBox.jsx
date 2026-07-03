'use client'
import { useState, useRef, useEffect } from 'react'
import { api } from '@/lib/api'
import { Send, Bot, User, Loader } from 'lucide-react'
import toast from 'react-hot-toast'

export default function AdminChatBox({ symbol }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: `Phase 8 Admin Interface active for ${symbol}. You can inject guidance, warnings, or domain expertise directly into the prediction model.` }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const userMsg = { role: 'user', content: input.trim() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    try {
      const res = await api.post('/api/admin/guidance', { message: input.trim(), symbol, context: messages.slice(-5) })
      setMessages(prev => [...prev, { role: 'assistant', content: res.data?.response || 'Guidance injected into model.' }])
    } catch {
      toast.error('Failed to send guidance')
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error processing guidance. Check backend connection.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-1.5" style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', fontWeight: 500 }}>
        <Bot size={13} />
        Admin Guidance Chat (Phase 8) — {symbol}
        <span className="live-badge ml-1">Live</span>
      </div>

      {/* Messages */}
      <div className="rounded-xl border p-3 flex flex-col gap-3 h-64 overflow-y-auto"
        style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}>
        {messages.map((msg, i) => (
          <div key={i} className={`flex items-start gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'assistant' ? 'chat-avatar-ai' : 'chat-avatar-user'}`}>
              {msg.role === 'assistant'
                ? <Bot  size={13} style={{ color: 'var(--bull-fg)' }} />
                : <User size={13} style={{ color: '#3B82F6' }} />}
            </div>
            <div className={`px-3 py-2 rounded-xl max-w-[80%] ${msg.role === 'assistant' ? 'rounded-tl-none' : 'rounded-tr-none'}`}
              style={{
                background: msg.role === 'assistant' ? 'var(--bg-card)' : '#2A7A6F',
                color: msg.role === 'assistant' ? 'var(--text-primary)' : '#fff',
                border: msg.role === 'assistant' ? '1px solid var(--border)' : 'none',
                fontSize: '0.88rem',
              }}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full chat-avatar-ai flex items-center justify-center">
              <Bot size={13} style={{ color: 'var(--bull-fg)' }} />
            </div>
            <div className="px-3 py-2 rounded-xl rounded-tl-none"
              style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--text-primary)' }}>
              <Loader size={13} className="animate-spin" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
          placeholder="Inject guidance… e.g. 'Reduce bull confidence for tech sector'"
          className="flex-1 px-3 py-2.5 rounded-xl border focus:outline-none focus:ring-2 focus:ring-[#2A7A6F]"
          style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-primary)', fontSize: '0.88rem' }}
        />
        <button onClick={sendMessage} disabled={!input.trim() || loading}
          className="px-3.5 py-2.5 rounded-xl text-white flex items-center justify-center transition-opacity disabled:opacity-50"
          style={{ background: '#2A7A6F' }}>
          <Send size={15} />
        </button>
      </div>
    </div>
  )
}
