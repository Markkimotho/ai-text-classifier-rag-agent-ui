import { useState, useCallback, useRef } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const TYPING_DELAY_MS = 30

export function useChat() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const typingRef = useRef(null)

  const appendMessage = useCallback((role, text, meta = {}) => {
    setMessages(prev => [...prev, { role, text, meta, id: Date.now() + Math.random() }])
  }, [])

  const typeMessage = useCallback((fullText, meta) => {
    let i = 0
    const id = Date.now() + Math.random()
    setMessages(prev => [...prev, { role: 'assistant', text: '', meta, id }])

    return new Promise(resolve => {
      typingRef.current = setInterval(() => {
        i++
        setMessages(prev =>
          prev.map(msg =>
            msg.id === id ? { ...msg, text: fullText.slice(0, i) } : msg
          )
        )
        if (i >= fullText.length) {
          clearInterval(typingRef.current)
          resolve()
        }
      }, TYPING_DELAY_MS)
    })
  }, [])

  const sendMessage = useCallback(async (question) => {
    if (!question.trim() || loading) return

    appendMessage('user', question)
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })

      if (!res.ok) throw new Error('Request failed')

      const data = await res.json()
      await typeMessage(data.answer, {
        sources: data.sources || [],
        tool_trace: data.tool_trace || [],
      })
    } catch {
      await typeMessage('Sorry, something went wrong. Please try again.', {})
    } finally {
      setLoading(false)
    }
  }, [loading, appendMessage, typeMessage])

  return { messages, loading, sendMessage }
}
