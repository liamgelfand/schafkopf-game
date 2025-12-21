import { useState, useEffect, useCallback, useRef } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import CardHand from './CardHand'
import TrickDisplay from './TrickDisplay'
import ContractSelector from './ContractSelector'
import ScoreDisplay from './ScoreDisplay'
import { Card as CardType, ContractType } from '../game/types'
import { GameWebSocket } from '../game/websocket'
import './GameBoard.css'

interface GameState {
  game_id: string
  current_trick: CardType[]
  current_player: number
  your_hand: CardType[]
  other_hands: (number | null)[]
  contract?: string
  trick_number: number
  round_complete: boolean
  players: string[]
}

function GameBoard() {
  const [searchParams] = useSearchParams()
  const roomId = searchParams.get('room') || ''
  const [gameState, setGameState] = useState<GameState | null>(null)
  const [selectedCard, setSelectedCard] = useState<CardType | null>(null)
  const [showContractSelector, setShowContractSelector] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const wsRef = useRef<GameWebSocket | null>(null)
  const userIdRef = useRef<string>('')

  useEffect(() => {
    // Get user ID from token
    const token = localStorage.getItem('token')
    if (!token) {
      setError('Not logged in')
      setLoading(false)
      return
    }

    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      userIdRef.current = payload.sub || 'unknown'  // Token uses username as "sub"
    } catch {
      userIdRef.current = 'unknown'
    }

    if (!roomId) {
      setError('No room ID provided')
      setLoading(false)
      return
    }

    // Connect WebSocket
    const ws = new GameWebSocket(roomId, userIdRef.current)
    wsRef.current = ws

    ws.connect((message) => {
      handleWebSocketMessage(message)
    })

    return () => {
      ws.disconnect()
    }
  }, [roomId])

  const handleWebSocketMessage = (message: any) => {
    setLoading(false)

    switch (message.type) {
      case 'game_state':
        const state = message.state
        setGameState({
          game_id: state.game_id,
          current_trick: state.current_trick || [],
          current_player: state.current_player,
          your_hand: state.your_hand || [],
          other_hands: state.other_hands || [],
          contract: state.contract,
          trick_number: state.trick_number || 0,
          round_complete: state.round_complete || false,
          players: state.players || [],
        })
        
        // Show contract selector if no contract set and it's your turn
        if (!state.contract && state.current_player === 0) {
          setShowContractSelector(true)
        } else {
          setShowContractSelector(false)
        }
        break

      case 'trick_complete':
        // Trick completed, wait for next state update
        break

      case 'player_passed':
        // Player passed, wait for state update
        break

      case 'contract_selected':
        setShowContractSelector(false)
        break

      case 'error':
        setError(message.message || 'An error occurred')
        break
    }
  }

  const handleCardClick = useCallback(
    (card: CardType) => {
      if (!gameState || gameState.current_player !== 0) {
        return // Not player's turn
      }

      if (!wsRef.current) return

      setSelectedCard(card)
      wsRef.current.playCard({
        suit: card.suit,
        rank: card.rank,
      })
      setSelectedCard(null)
    },
    [gameState]
  )

  const handlePass = useCallback(async () => {
    if (!gameState || gameState.current_player !== 0) {
      return
    }

    if (wsRef.current) {
      wsRef.current.pass()
    }
  }, [gameState])

  const handleContractSelect = useCallback(
    (contract: ContractType, calledAce?: string, trumpSuit?: string) => {
      if (!wsRef.current) return

      wsRef.current.selectContract(contract, trumpSuit, calledAce)
      setShowContractSelector(false)
    },
    []
  )

  if (loading) {
    return (
      <div className="game-board">
        <div className="game-start">
          <h2>Connecting to game...</h2>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="game-board">
        <div className="game-start">
          <h2>Error</h2>
          <p>{error}</p>
          <Link to="/lobby" className="back-link">
            Back to Lobby
          </Link>
        </div>
      </div>
    )
  }

  if (!gameState) {
    return (
      <div className="game-board">
        <div className="game-start">
          <h2>Waiting for game to start...</h2>
        </div>
      </div>
    )
  }

  const playerHand = gameState.your_hand || []
  const isPlayerTurn = gameState.current_player === 0 && !showContractSelector
  const playerNames = gameState.players || ['Player 1', 'Player 2', 'Player 3', 'Player 4']

  return (
    <div className="game-board">
      <div className="game-header">
        <h2>Schafkopf Game</h2>
        {gameState.contract && (
          <div className="contract-info">
            Contract: <strong>{gameState.contract}</strong>
          </div>
        )}
        <div className="trick-info">
          Trick {gameState.trick_number}/8
        </div>
      </div>

      {showContractSelector && (
        <ContractSelector
          onSelect={handleContractSelect}
          playerHand={playerHand}
          disabled={false}
        />
      )}

      <TrickDisplay
        trick={gameState.current_trick}
        currentPlayerIndex={gameState.current_player}
        playerNames={playerNames}
      />

      <div className="player-info">
        <div className="current-turn">
          {isPlayerTurn ? (
            <span className="your-turn">Your Turn</span>
          ) : (
            <span>
              {playerNames[gameState.current_player] || 'Unknown'}'s Turn
            </span>
          )}
        </div>
        <div className="other-players">
          {gameState.other_hands.map((handSize, index) => {
            if (index === 0) return null // Skip self
            return (
              <div key={index} className="other-player">
                {playerNames[index]}: {handSize !== null ? `${handSize} cards` : '?'}
              </div>
            )
          })}
        </div>
      </div>

      <div className="player-hand-section">
        <h3>Your Hand</h3>
        <CardHand
          cards={playerHand}
          onCardClick={handleCardClick}
          disabled={!isPlayerTurn || gameState.round_complete}
          selectedCard={selectedCard}
          sortable={true}
          autoSort={true}
        />
        {isPlayerTurn && !gameState.round_complete && (
          <div className="game-actions">
            <button onClick={handlePass} className="pass-button">
              Pass
            </button>
          </div>
        )}
      </div>

      <Link to="/lobby" className="back-link">
        Back to Lobby
      </Link>
    </div>
  )
}

export default GameBoard
