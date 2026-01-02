import { Card as CardType } from '../game/types'
import './Card.css'

interface CardProps {
  card: CardType
  onClick?: () => void
  disabled?: boolean
  selected?: boolean
}

function Card({ card, onClick, disabled = false, selected = false }: CardProps) {
  const rankDisplay: Record<string, string> = {
    Ace: 'A',
    King: 'K',
    Ober: 'O',
    Unter: 'U',
    Ten: '10',
    Nine: '9',
    Eight: '8',
    Seven: '7',
  }

  const suitNames: Record<string, string> = {
    Eichel: 'Eichel',
    Gras: 'Gras',
    Herz: 'Herz',
    Schellen: 'Schellen'
  }

  const isRed = card.suit === 'Herz' || card.suit === 'Schellen'

  return (
    <div
      className={`card ${disabled ? 'disabled' : ''} ${selected ? 'selected' : ''} ${isRed ? 'red-suit' : 'black-suit'}`}
      onClick={disabled ? undefined : onClick}
    >
      <div className="card-content">
        <div className="card-rank">{rankDisplay[card.rank]}</div>
        <div className="card-suit">{suitNames[card.suit]}</div>
      </div>
    </div>
  )
}

export default Card
