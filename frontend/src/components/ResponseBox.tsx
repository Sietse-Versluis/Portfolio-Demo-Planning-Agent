import { useEffect, useRef, useState } from 'react'
import './ResponseBox.css'

type Phase = 'idle' | 'loading' | 'done'

interface Props {
  phase: Phase
  response: string
}

const LOADING_DOTS = ['Thinking', 'Thinking.', 'Thinking..', 'Thinking...']

export default function ResponseBox({ phase, response }: Props) {
  const [visible, setVisible] = useState(false)
  const [dotIndex, setDotIndex] = useState(0)
  const dotTimer = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (phase === 'loading' || phase === 'done') {
      setVisible(true)
    } else {
      setVisible(false)
    }
  }, [phase])

  useEffect(() => {
    if (phase === 'loading') {
      setDotIndex(0)
      dotTimer.current = setInterval(() => {
        setDotIndex(i => (i + 1) % LOADING_DOTS.length)
      }, 400)
    } else {
      if (dotTimer.current) clearInterval(dotTimer.current)
    }
    return () => {
      if (dotTimer.current) clearInterval(dotTimer.current)
    }
  }, [phase])

  return (
    <div className={`response-wrap ${visible ? 'response-wrap--visible' : ''}`}>
      <div className="response-box">
        {phase === 'loading' && (
          <span className="response-loading">{LOADING_DOTS[dotIndex]}</span>
        )}
        {phase === 'done' && (
          <span className="response-text">{response}</span>
        )}
      </div>
    </div>
  )
}
