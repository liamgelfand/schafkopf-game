// Game type definitions
export type Suit = 'Eichel' | 'Gras' | 'Herz' | 'Schellen'
export type Rank = 'Ace' | 'King' | 'Ober' | 'Unter' | 'Ten' | 'Nine' | 'Eight' | 'Seven'

export interface Card {
  suit: Suit
  rank: Rank
  value: number
}

export type ContractType = 'Rufer' | 'Wenz' | 'Solo'

export interface GameState {
  players: Player[]
  currentTrick: Card[]
  currentPlayer: number
  contract?: ContractType
  declarer?: number
  partner?: number
  round: number
  scores: number[]
}

export interface Player {
  id: number
  name: string
  hand: Card[]
  isAI: boolean
}


