import { useState, useEffect, useCallback, useRef } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import CardHand from './CardHand'
import Card from './Card'
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
  your_player_index?: number
  bidding_phase?: boolean
  current_bidder?: number
  highest_bid?: {
    contract_type: string
    trump_suit?: string
    called_ace?: string
    bidder_index: number
  } | null
  passes_in_a_row?: number
}

function GameBoard() {
  const [searchParams] = useSearchParams()
  const roomId = searchParams.get('room') || ''
  const [gameState, setGameState] = useState<GameState | null>(null)
  const [selectedCard, setSelectedCard] = useState<CardType | null>(null)
  const [selectedContract, setSelectedContract] = useState<string>('')
  const [selectedTrump, setSelectedTrump] = useState<string>('')
  const [selectedCalledAce, setSelectedCalledAce] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [playError, setPlayError] = useState<string | null>(null)
  const wsRef = useRef<GameWebSocket | null>(null)
  const userIdRef = useRef<string>('')

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      setError('Not logged in')
      setLoading(false)
      return
    }

    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      userIdRef.current = payload.sub || 'unknown'
    } catch {
      userIdRef.current = 'unknown'
    }

    if (!roomId) {
      setError('No room ID provided')
      setLoading(false)
      return
    }

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
        const receivedPlayerIndex = state.your_player_index
        console.log('Received game state:', {
          players: state.players,
          your_player_index: receivedPlayerIndex,
          your_hand_length: state.your_hand?.length,
          other_hands: state.other_hands,
          current_bidder: state.current_bidder,
          bidding_phase: state.bidding_phase
        })
        
        // Validate your_player_index is set
        if (receivedPlayerIndex === undefined || receivedPlayerIndex === null) {
          console.error('your_player_index is missing from game state!', state)
          // Request state again if player index is missing
          if (wsRef.current) {
            console.log('Requesting state again due to missing player index')
            setTimeout(() => wsRef.current?.getState(), 500)
          }
        }
        
        // Always update state - don't preserve old player_index if new one is provided
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
          your_player_index: receivedPlayerIndex !== undefined && receivedPlayerIndex !== null 
            ? receivedPlayerIndex 
            : 0, // Default to 0 if not set (shouldn't happen)
          bidding_phase: state.bidding_phase || false,
          current_bidder: state.current_bidder,
          highest_bid: state.highest_bid || null,
          passes_in_a_row: state.passes_in_a_row || 0,
        })
        break
      
      case 'game_not_ready':
        console.log('Game not ready yet:', message.message)
        setLoading(true)
        // Request state again in a moment
        if (wsRef.current) {
          setTimeout(() => wsRef.current?.getState(), 1000)
        }
        break
      
      case 'game_state_update':
        // Game state was updated, request fresh state
        console.log('Game state updated, requesting fresh state')
        if (wsRef.current) {
          wsRef.current.getState()
        }
        break

      case 'bid_made':
      case 'bid_passed':
      case 'bidding_complete':
        if (wsRef.current) {
          wsRef.current.getState()
        }
        break
      
      case 'all_passed':
      case 'cards_reshuffled':
        console.log('Cards reshuffled, new bidding round')
        if (wsRef.current) {
          wsRef.current.getState()
        }
        break

      case 'trick_complete':
        if (wsRef.current) {
          wsRef.current.getState()
        }
        break

      case 'error':
        // Only set error for critical errors that should block the UI
        if (message.message && !message.message.includes('Not your turn') && !message.message.includes('Cannot play')) {
          setError(message.message || 'An error occurred')
        }
        break
      
      case 'play_error':
        // Show play error as a temporary notification, don't disconnect
        setPlayError(message.message || 'Cannot play this card')
        console.log('Play error:', message.message)
        // Clear error after 5 seconds
        setTimeout(() => setPlayError(null), 5000)
        break
    }
  }

  const handleCardClick = useCallback(
    (card: CardType) => {
      if (!gameState) {
        console.log('Cannot play card: no game state')
        return
      }
      
      // Only allow card play if not in bidding phase and it's your turn
      const yourIndex = gameState.your_player_index ?? 0
      console.log('Card click:', {
        card: `${card.suit} ${card.rank}`,
        yourIndex,
        currentPlayer: gameState.current_player,
        biddingPhase: gameState.bidding_phase,
        isYourTurn: !gameState.bidding_phase && gameState.current_player === yourIndex
      })
      
      if (gameState.bidding_phase) {
        console.log('Cannot play card: still in bidding phase')
        return
      }
      
      if (gameState.current_player !== yourIndex) {
        console.log(`Cannot play card: not your turn. Current player: ${gameState.current_player}, You are: ${yourIndex}`)
        return
      }

      if (!wsRef.current) {
        console.log('Cannot play card: WebSocket not connected')
        return
      }

      console.log(`Playing card: ${card.suit} ${card.rank}`)
      setSelectedCard(card)
      wsRef.current.playCard({
        suit: card.suit,
        rank: card.rank,
      })
      setSelectedCard(null)
    },
    [gameState]
  )

  const handleBid = useCallback(() => {
    if (!gameState || !wsRef.current) return
    
    // Get your player index from state
    const yourIndex = gameState.your_player_index ?? 0
    if (gameState.current_bidder !== yourIndex) {
      console.log(`Not your turn to bid. Current bidder: ${gameState.current_bidder}, You are: ${yourIndex}`)
      return
    }
    if (!selectedContract) {
      console.log('No contract selected')
      return
    }

    console.log('Making bid:', { contract: selectedContract, trump: selectedTrump, calledAce: selectedCalledAce })
    wsRef.current.selectContract(
      selectedContract as ContractType,
      selectedTrump || undefined,
      selectedCalledAce || undefined
    )
    setSelectedContract('')
    setSelectedTrump('')
    setSelectedCalledAce('')
  }, [gameState, selectedContract, selectedTrump, selectedCalledAce])

  const handlePassBid = useCallback(() => {
    if (!gameState || !wsRef.current) return
    
    // Get your player index from state
    const yourIndex = gameState.your_player_index ?? 0
    if (gameState.current_bidder !== yourIndex) {
      console.log(`Not your turn to pass. Current bidder: ${gameState.current_bidder}, You are: ${yourIndex}`)
      return
    }

    console.log('Passing bid')
    wsRef.current.pass()
  }, [gameState])

  const getContractRank = (contractType: string, trumpSuit?: string): number => {
    // Contract hierarchy (lowest to highest):
    // 1. Rufer
    // 2. Wenz (no suit)
    // 3. Suited Wenz (with suit)
    // 4. Solo (all suits equal value)
    if (contractType === 'Rufer') return 1
    if (contractType === 'Wenz') {
      // If trumpSuit is provided, it's a Suited Wenz
      return trumpSuit ? 3 : 2
    }
    if (contractType === 'Solo') {
      // All Solo suits are equal value (rank 4)
      return 4
    }
    return 0
  }

  const canBid = (contractType: string, trumpSuit?: string): boolean => {
    if (!gameState?.highest_bid) return true
    const currentRank = getContractRank(
      gameState.highest_bid.contract_type,
      gameState.highest_bid.trump_suit
    )
    const newRank = getContractRank(contractType, trumpSuit)
    // Must bid higher than current highest
    // If same rank (e.g., both Solo), cannot override (first bidder wins)
    return newRank > currentRank
  }

  if (loading) {
    return (
      <div className="game-board">
        <div className="game-loading">Connecting to game...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="game-board">
        <div className="game-error">
          <h2>Error</h2>
          <p>{error}</p>
          <Link to="/lobby">Back to Lobby</Link>
        </div>
      </div>
    )
  }

  if (!gameState) {
    return (
      <div className="game-board">
        <div className="game-loading">Waiting for game to start...</div>
      </div>
    )
  }

  const playerHand = gameState.your_hand || []
  const playerNames = gameState.players || ['Player 1', 'Player 2', 'Player 3', 'Player 4']
  
  // CRITICAL: Get your_player_index - if not set, try to infer from other_hands
  let yourPlayerIndex = gameState.your_player_index
  if (yourPlayerIndex === undefined || yourPlayerIndex === null) {
    // Try to infer from other_hands (the one with None is your hand)
    const noneIndex = gameState.other_hands?.findIndex((h: number | null) => h === null)
    if (noneIndex !== undefined && noneIndex !== -1) {
      yourPlayerIndex = noneIndex
      console.log(`Inferred your_player_index from other_hands: ${yourPlayerIndex}`)
    } else {
      yourPlayerIndex = 0
      console.warn('your_player_index is undefined and could not be inferred, defaulting to 0')
    }
  }
  
  // Debug logging
  console.log('Rendering GameBoard:', {
    yourPlayerIndex,
    your_player_index_from_state: gameState.your_player_index,
    playerNames,
    yourHandSize: playerHand.length,
    otherHands: gameState.other_hands,
    currentUsername: userIdRef.current
  })
  
  const isBiddingPhase = gameState.bidding_phase && !gameState.contract
  const isYourBidTurn = isBiddingPhase && gameState.current_bidder === yourPlayerIndex
  const isYourPlayTurn = !isBiddingPhase && gameState.current_player === yourPlayerIndex && !gameState.round_complete

  return (
    <div className="game-board">
      <div className="game-header">
        <h2>Schafkopf</h2>
        {gameState.contract && (
          <div className="contract-display">Contract: {gameState.contract}</div>
        )}
        {!isBiddingPhase && (
          <div className="trick-counter">Trick {gameState.trick_number}/8</div>
        )}
      </div>

      <div className="game-table">
        {/* Top Player - index 2 relative to you (index 0) */}
        <div className={`player-seat player-top ${gameState.current_bidder === (yourPlayerIndex + 2) % 4 || (!isBiddingPhase && gameState.current_player === (yourPlayerIndex + 2) % 4) ? 'active' : ''}`}>
          <div className="player-name">{playerNames[(yourPlayerIndex + 2) % 4] || 'Player 3'}</div>
          <div className="player-cards">
            {gameState.other_hands[(yourPlayerIndex + 2) % 4] !== null ? `${gameState.other_hands[(yourPlayerIndex + 2) % 4]} cards` : '?'}
          </div>
        </div>

        {/* Left Player - index 3 relative to you */}
        <div className={`player-seat player-left ${gameState.current_bidder === (yourPlayerIndex + 3) % 4 || (!isBiddingPhase && gameState.current_player === (yourPlayerIndex + 3) % 4) ? 'active' : ''}`}>
          <div className="player-name">{playerNames[(yourPlayerIndex + 3) % 4] || 'Player 4'}</div>
          <div className="player-cards">
            {gameState.other_hands[(yourPlayerIndex + 3) % 4] !== null ? `${gameState.other_hands[(yourPlayerIndex + 3) % 4]} cards` : '?'}
          </div>
        </div>

        {/* Right Player - index 1 relative to you */}
        <div className={`player-seat player-right ${gameState.current_bidder === (yourPlayerIndex + 1) % 4 || (!isBiddingPhase && gameState.current_player === (yourPlayerIndex + 1) % 4) ? 'active' : ''}`}>
          <div className="player-name">{playerNames[(yourPlayerIndex + 1) % 4] || 'Player 2'}</div>
          <div className="player-cards">
            {gameState.other_hands[(yourPlayerIndex + 1) % 4] !== null ? `${gameState.other_hands[(yourPlayerIndex + 1) % 4]} cards` : '?'}
          </div>
        </div>

        {/* Center - Trick Display */}
        <div className="table-center">
          {isBiddingPhase ? (
            <div className="bidding-status">
              <div className="current-bidder">
                {gameState.current_bidder === yourPlayerIndex ? 'Your turn to bid' : `${playerNames[gameState.current_bidder ?? 0]}'s turn`}
              </div>
              {gameState.highest_bid && (
                <div className="highest-bid">
                  Highest: {gameState.highest_bid.contract_type}
                  {gameState.highest_bid.trump_suit && ` ${gameState.highest_bid.trump_suit}`}
                </div>
              )}
              <div className="passes-count">Passes: {gameState.passes_in_a_row}/3</div>
            </div>
          ) : (
            <div className="trick-display">
              {gameState.current_trick.map((card, idx) => (
                <Card key={idx} card={card} disabled={true} />
              ))}
              {gameState.current_trick.length === 0 && (
                <div className="empty-trick">No cards played yet</div>
              )}
            </div>
          )}
        </div>

        {/* Bottom Player - You */}
        <div className={`player-seat player-bottom ${isYourBidTurn || isYourPlayTurn ? 'active' : ''}`}>
          <div className="player-name">You ({playerNames[yourPlayerIndex]})</div>
        </div>
      </div>

      {/* Bidding UI - Show cards during bidding so players can decide */}
      {isBiddingPhase && (
        <div className="your-hand-section">
          <h3>Your Hand - Choose Your Bid</h3>
          <CardHand
            cards={playerHand}
            onCardClick={() => {}} // Cards not clickable during bidding
            disabled={true}
            selectedCard={null}
            sortable={true}
            autoSort={true}
          />
        </div>
      )}

      {isBiddingPhase && isYourBidTurn && (
        <div className="bidding-panel">
          <h3>Make Your Bid</h3>
          <div className="contract-options">
            <button
              className={`contract-btn ${selectedContract === 'Rufer' ? 'selected' : ''} ${!canBid('Rufer') ? 'disabled' : ''}`}
              onClick={() => setSelectedContract('Rufer')}
              disabled={!canBid('Rufer')}
            >
              Rufer
            </button>
            <div className="wenz-group">
              <span>Wenz:</span>
              <button
                className={`contract-btn ${selectedContract === 'Wenz' && !selectedTrump ? 'selected' : ''} ${!canBid('Wenz') ? 'disabled' : ''}`}
                onClick={() => {
                  setSelectedContract('Wenz')
                  setSelectedTrump('')
                }}
                disabled={!canBid('Wenz')}
              >
                Wenz (Regular)
              </button>
              {['Eichel', 'Gras', 'Herz', 'Schellen'].map(suit => (
                <button
                  key={suit}
                  className={`contract-btn wenz-suited ${selectedContract === 'Wenz' && selectedTrump === suit ? 'selected' : ''} ${!canBid('Wenz', suit) ? 'disabled' : ''}`}
                  onClick={() => {
                    setSelectedContract('Wenz')
                    setSelectedTrump(suit)
                  }}
                  disabled={!canBid('Wenz', suit)}
                >
                  Wenz {suit}
                </button>
              ))}
            </div>
            <div className="solo-group">
              <span>Solo:</span>
              {['Eichel', 'Gras', 'Herz', 'Schellen'].map(suit => (
                <button
                  key={suit}
                  className={`contract-btn solo ${selectedContract === 'Solo' && selectedTrump === suit ? 'selected' : ''} ${!canBid('Solo', suit) ? 'disabled' : ''}`}
                  onClick={() => {
                    setSelectedContract('Solo')
                    setSelectedTrump(suit)
                  }}
                  disabled={!canBid('Solo', suit)}
                >
                  Solo {suit}
                </button>
              ))}
            </div>
          </div>
          {selectedContract === 'Rufer' && (
            <div className="called-ace-select">
              <label>Call Ace:</label>
              <select value={selectedCalledAce} onChange={(e) => setSelectedCalledAce(e.target.value)}>
                <option value="">Select...</option>
                {['Eichel', 'Gras', 'Herz', 'Schellen'].map(suit => (
                  <option key={suit} value={suit}>{suit}</option>
                ))}
              </select>
            </div>
          )}
          <div className="bidding-actions">
            <button
              className="bid-btn"
              onClick={handleBid}
              disabled={!selectedContract || (selectedContract === 'Rufer' && !selectedCalledAce)}
            >
              Make Bid
            </button>
            <button className="pass-btn" onClick={handlePassBid}>
              Pass
            </button>
          </div>
        </div>
      )}

      {/* Your Hand */}
      {!isBiddingPhase && (
        <div className="your-hand-section">
          <CardHand
            cards={playerHand}
            onCardClick={handleCardClick}
            disabled={!isYourPlayTurn}
            selectedCard={selectedCard}
            sortable={true}
            autoSort={true}
          />
        </div>
      )}

      <Link to="/lobby" className="back-link">
        Back to Lobby
      </Link>

      {/* Play Error Toast */}
      {playError && (
        <div className="play-error-toast" onClick={() => setPlayError(null)}>
          <div className="play-error-content">
            <strong>Cannot Play Card</strong>
            <p>{playError}</p>
            <button className="close-error-btn" onClick={(e) => { e.stopPropagation(); setPlayError(null); }}>
              ×
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default GameBoard

