import './SuitIcon.css'

interface SuitIconProps {
  suit: 'Eichel' | 'Gras' | 'Herz' | 'Schellen'
  size?: 'small' | 'medium' | 'large'
}

function SuitIcon({ suit, size = 'medium' }: SuitIconProps) {
  const sizeClass = `suit-icon-${size}`
  
  // Authentic German card suit symbols
  const getSuitSVG = () => {
    switch (suit) {
      case 'Eichel':
        // Acorn - German playing card style
        return (
          <svg viewBox="0 0 100 120" className={sizeClass} preserveAspectRatio="xMidYMid meet">
            <path d="M50 10 Q45 15 45 25 L45 50 Q45 60 50 65 Q55 60 55 50 L55 25 Q55 15 50 10 Z" fill="currentColor"/>
            <path d="M50 65 Q40 70 35 80 Q30 90 35 100 Q40 105 50 105 Q60 105 65 100 Q70 90 65 80 Q60 70 50 65 Z" fill="currentColor"/>
            <path d="M50 105 L45 110 L50 115 L55 110 Z" fill="currentColor"/>
          </svg>
        )
      case 'Gras':
        // Leaves/Grass - German playing card style
        return (
          <svg viewBox="0 0 100 120" className={sizeClass} preserveAspectRatio="xMidYMid meet">
            <path d="M50 10 L45 30 Q40 50 50 60 Q60 50 55 30 Z" fill="currentColor"/>
            <path d="M50 60 L40 80 Q35 100 50 110 Q65 100 60 80 Z" fill="currentColor"/>
            <path d="M30 70 Q25 75 30 85 Q35 80 30 70" fill="currentColor"/>
            <path d="M70 70 Q75 75 70 85 Q65 80 70 70" fill="currentColor"/>
          </svg>
        )
      case 'Herz':
        // Heart - standard
        return (
          <svg viewBox="0 0 100 120" className={sizeClass} preserveAspectRatio="xMidYMid meet">
            <path d="M50 30 Q40 20 30 30 Q20 40 30 55 Q40 70 50 85 Q60 70 70 55 Q80 40 70 30 Q60 20 50 30 Z" fill="currentColor"/>
          </svg>
        )
      case 'Schellen':
        // Bells - German playing card style
        return (
          <svg viewBox="0 0 100 120" className={sizeClass} preserveAspectRatio="xMidYMid meet">
            <path d="M50 15 Q40 20 35 30 Q30 40 35 50 Q40 60 50 65 Q60 60 65 50 Q70 40 65 30 Q60 20 50 15 Z" fill="currentColor"/>
            <path d="M50 65 L45 75 L50 85 L55 75 Z" fill="currentColor"/>
            <circle cx="50" cy="40" r="8" fill="white"/>
            <path d="M50 30 L50 50" stroke="white" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        )
      default:
        return null
    }
  }

  return (
    <span className={`suit-icon suit-${suit.toLowerCase()}`}>
      {getSuitSVG()}
    </span>
  )
}

export default SuitIcon
