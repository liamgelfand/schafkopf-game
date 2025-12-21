import { useState, useCallback } from 'react'
import { GameState } from '../game/types'

export function useGameState() {
  const [gameState, setGameState] = useState<GameState | null>(null)

  const updateGameState = useCallback((newState: GameState) => {
    setGameState(newState)
  }, [])

  return {
    gameState,
    updateGameState,
  }
}


