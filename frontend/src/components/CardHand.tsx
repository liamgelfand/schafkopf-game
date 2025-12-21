import { useState } from 'react'
import { Card as CardType } from '../game/types'
import Card from './Card'
import './CardHand.css'

interface CardHandProps {
  cards: CardType[]
  onCardClick?: (card: CardType) => void
  disabled?: boolean
  selectedCard?: CardType | null
  sortable?: boolean
  autoSort?: boolean
}

type SortMode = 'suit' | 'rank' | 'trump' | 'custom'

function CardHand({ 
  cards, 
  onCardClick, 
  disabled = false, 
  selectedCard = null,
  sortable = true,
  autoSort = true
}: CardHandProps) {
  const [sortMode, setSortMode] = useState<SortMode>('suit')
  const [customOrder, setCustomOrder] = useState<CardType[]>([])

  // Auto-sort cards optimally for Schafkopf
  const sortCards = (cardsToSort: CardType[], mode: SortMode): CardType[] => {
    const sorted = [...cardsToSort]
    
    switch (mode) {
      case 'suit':
        // Sort by suit (Eichel, Gras, Herz, Schellen), then by rank
        const suitOrder: Record<string, number> = { Eichel: 0, Gras: 1, Herz: 2, Schellen: 3 }
        const rankOrder: Record<string, number> = {
          Ace: 0, Ten: 1, King: 2, Ober: 3, Unter: 4, Nine: 5, Eight: 6, Seven: 7
        }
        return sorted.sort((a, b) => {
          if (suitOrder[a.suit] !== suitOrder[b.suit]) {
            return suitOrder[a.suit] - suitOrder[b.suit]
          }
          return rankOrder[a.rank] - rankOrder[b.rank]
        })
      
      case 'rank':
        // Sort by rank, then suit
        return sorted.sort((a, b) => {
          if (rankOrder[a.rank] !== rankOrder[b.rank]) {
            return rankOrder[a.rank] - rankOrder[b.rank]
          }
          return suitOrder[a.suit] - suitOrder[b.suit]
        })
      
      case 'trump':
        // Put trumps first (Obers, Unters, Hearts), then others
        const isTrump = (card: CardType) => 
          card.rank === 'Ober' || card.rank === 'Unter' || card.suit === 'Herz'
        return sorted.sort((a, b) => {
          const aTrump = isTrump(a)
          const bTrump = isTrump(b)
          if (aTrump !== bTrump) return aTrump ? -1 : 1
          return suitOrder[a.suit] - suitOrder[b.suit]
        })
      
      case 'custom':
        return customOrder.length > 0 ? customOrder : sorted
      
      default:
        return sorted
    }
  }

  const displayCards = autoSort ? sortCards(cards, sortMode) : cards

  const handleSortChange = (mode: SortMode) => {
    setSortMode(mode)
    if (mode === 'custom') {
      setCustomOrder([...cards])
    }
  }

  return (
    <div className="card-hand-container">
      {sortable && (
        <div className="card-sort-controls">
          <label>Sort:</label>
          <select 
            value={sortMode} 
            onChange={(e) => handleSortChange(e.target.value as SortMode)}
            className="sort-select"
          >
            <option value="suit">By Suit</option>
            <option value="rank">By Rank</option>
            <option value="trump">Trumps First</option>
            <option value="custom">Custom</option>
          </select>
        </div>
      )}
      <div className="card-hand">
        {displayCards.map((card, index) => (
          <Card
            key={`${card.suit}-${card.rank}-${index}`}
            card={card}
            onClick={() => onCardClick?.(card)}
            disabled={disabled}
            selected={selectedCard?.suit === card.suit && selectedCard?.rank === card.rank}
          />
        ))}
      </div>
    </div>
  )
}

export default CardHand
