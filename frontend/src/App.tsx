import { useState, useCallback } from 'react'
import ChatInput from './components/ChatInput'
import ResponseBox from './components/ResponseBox'
import './App.css'

type Phase = 'idle' | 'loading' | 'done'

export default function App() {
  const [phase, setPhase] = useState<Phase>('idle')
  const [response, setResponse] = useState('')

  const handleSubmit = useCallback(async (question: string) => {
    setPhase('loading')
    setResponse('')

    try {
      const res = await fetch('/api/agent/question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })
      const data = await res.json()
      setResponse(typeof data === 'string' ? data : data.message ?? JSON.stringify(data))
    } catch {
      setResponse('Something went wrong. Please try again.')
    }

    setPhase('done')
  }, [])

  const handleReset = useCallback(() => {
    setPhase('idle')
    setResponse('')
  }, [])

  return (
    <div className="page">
      <ChatInput
        onSubmit={handleSubmit}
        onFocusWhenDone={handleReset}
        isActive={phase !== 'idle'}
      />
      <ResponseBox phase={phase} response={response} />
    </div>
  )
}
