import { Card as CardType } from '../game/types'
import Card from './Card'
import './TrickDisplay.css'

interface TrickDisplayProps {
  trick: CardType[]
  currentPlayerIndex: number
  playerNames: string[]
}

function TrickDisplay({ trick, currentPlayerIndex, playerNames }: TrickDisplayProps) {
  if (trick.length === 0) {
    return <div className="trick-display empty">No cards played yet</div>
  }

  return (
    <div className="trick-display">
      <h3>Current Trick</h3>
      <div className="trick-cards">
        {trick.map((card, index) => {
          const playerIndex = (currentPlayerIndex - trick.length + index + 4) % 4
          return (
            <div key={index} className="trick-card-wrapper">
              <Card card={card} disabled />
              <div className="trick-player-name">{playerNames[playerIndex]}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default TrickDisplay


