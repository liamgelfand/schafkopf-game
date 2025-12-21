import { Card as CardType } from '../game/types'
import SuitIcon from './SuitIcon'
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

  const isRed = card.suit === 'Herz' || card.suit === 'Schellen'

  return (
    <div
      className={`card ${disabled ? 'disabled' : ''} ${selected ? 'selected' : ''} ${isRed ? 'red-suit' : 'black-suit'}`}
      onClick={disabled ? undefined : onClick}
    >
      <div className="card-corner card-corner-top">
        <div className="card-rank">{rankDisplay[card.rank]}</div>
        <SuitIcon suit={card.suit} size="small" />
      </div>
      <div className="card-center">
        <SuitIcon suit={card.suit} size="large" />
      </div>
      <div className="card-corner card-corner-bottom">
        <div className="card-rank">{rankDisplay[card.rank]}</div>
        <SuitIcon suit={card.suit} size="small" />
      </div>
      {card.value > 0 && (
        <div className="card-points">{card.value}</div>
      )}
    </div>
  )
}

export default Card

