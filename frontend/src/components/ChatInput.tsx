import { useEffect, useRef, useState, useCallback } from 'react'
import SubmitButton from './SubmitButton'
import './ChatInput.css'

const EXAMPLES = [
  'Plan a team meeting tomorrow at 10:00',
  'Add a dentist appointment on Friday at 14:30',
  'What do I have scheduled this week?',
  'Move my Monday standup to 9:00',
  'Delete the gym session on Thursday',
]

interface Props {
  onSubmit: (value: string) => void
  onFocusWhenDone: () => void
  isActive: boolean
}

export default function ChatInput({ onSubmit, onFocusWhenDone, isActive }: Props) {
  const [value, setValue] = useState('')
  const [placeholder, setPlaceholder] = useState('')
  const [userFocused, setUserFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  // Typing animation state
  const exampleIndexRef = useRef(0)
  const charIndexRef = useRef(0)
  const deletingRef = useRef(false)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const stopAnimation = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
  }, [])

  const tick = useCallback(() => {
    if (userFocused || isActive) return

    const current = EXAMPLES[exampleIndexRef.current]

    if (!deletingRef.current) {
      if (charIndexRef.current < current.length) {
        charIndexRef.current++
        setPlaceholder(current.slice(0, charIndexRef.current))
        timerRef.current = setTimeout(tick, 45)
      } else {
        timerRef.current = setTimeout(() => {
          deletingRef.current = true
          tick()
        }, 1800)
      }
    } else {
      if (charIndexRef.current > 0) {
        charIndexRef.current--
        setPlaceholder(current.slice(0, charIndexRef.current))
        timerRef.current = setTimeout(tick, 25)
      } else {
        deletingRef.current = false
        exampleIndexRef.current = (exampleIndexRef.current + 1) % EXAMPLES.length
        timerRef.current = setTimeout(tick, 400)
      }
    }
  }, [userFocused, isActive])

  useEffect(() => {
    if (!userFocused && !isActive) {
      timerRef.current = setTimeout(tick, 600)
    } else {
      stopAnimation()
      if (!isActive) setPlaceholder('')
    }
    return stopAnimation
  }, [userFocused, isActive, tick, stopAnimation])

  const handleFocus = () => {
    if (isActive) {
      onFocusWhenDone()
      setValue('')
    }
    setUserFocused(true)
  }

  const handleBlur = () => {
    if (value === '') setUserFocused(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && value.trim()) {
      e.preventDefault()
      submit()
    }
  }

  const submit = () => {
    const trimmed = value.trim()
    if (!trimmed) return
    onSubmit(trimmed)
    setUserFocused(false)
    if (inputRef.current) inputRef.current.blur()
  }

  return (
    <div className="chat-input-wrapper">
      <div className={`chat-input-row ${isActive ? 'submitted' : ''}`}>
        <input
          ref={inputRef}
          className={`chat-input${isActive ? ' chat-input--submitted' : ''}`}
          type="text"
          value={value}
          placeholder={userFocused ? 'Ask your calendar agent...' : placeholder}
          onChange={e => !isActive && setValue(e.target.value)}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          autoComplete="off"
          spellCheck={false}
          readOnly={isActive}
        />
        <SubmitButton onClick={submit} disabled={!value.trim()} />
      </div>
    </div>
  )
}
