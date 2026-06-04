import './SubmitButton.css'

interface Props {
  onClick: () => void
  disabled: boolean
}

export default function SubmitButton({ onClick, disabled }: Props) {
  return (
    <button
      className="submit-btn"
      onClick={onClick}
      disabled={disabled}
      aria-label="Submit"
    >
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <line x1="12" y1="19" x2="12" y2="5" />
        <polyline points="5 12 12 5 19 12" />
      </svg>
    </button>
  )
}
