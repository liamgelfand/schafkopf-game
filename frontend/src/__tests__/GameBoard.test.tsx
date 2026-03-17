import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import GameBoard from '../components/GameBoard'
import { GameWebSocket } from '../game/websocket'

// Create a valid JWT token mock (header.payload.signature)
const createMockToken = (username: string = 'testuser') => {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const payload = btoa(JSON.stringify({ sub: username, exp: Date.now() / 1000 + 3600 }))
  const signature = 'mock-signature'
  return `${header}.${payload}.${signature}`
}

// Mock WebSocket class
class MockWebSocket {
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  onclose: (() => void) | null = null
  readyState = WebSocket.CONNECTING
  url: string = ''
  
  constructor(url: string) {
    this.url = url
    // Simulate connection opening
    setTimeout(() => {
      this.readyState = WebSocket.OPEN
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    }, 10)
  }
  
  send(_data: string) {
    // Mock send
  }
  
  close() {
    this.readyState = WebSocket.CLOSED
    if (this.onclose) {
      this.onclose()
    }
  }
}

// Store message callback globally for test access
let globalMessageCallback: ((message: any) => void) | null = null

// Mock GameWebSocket class
vi.mock('../game/websocket', () => {
  return {
    GameWebSocket: class MockGameWebSocket {
      private gameId: string
      private onMessageCallback?: (message: any) => void

      constructor(gameId: string, userId: string) {
        this.gameId = gameId
      }

      connect(onMessage: (message: any) => void) {
        this.onMessageCallback = onMessage
        globalMessageCallback = onMessage
        // Simulate connection and initial state request
        setTimeout(() => {
          if (globalMessageCallback) {
            globalMessageCallback({ type: 'game_not_ready' })
          }
        }, 50)
      }

      send(message: any) {
        // Mock send - can be used to verify calls
      }

      playCard(card: { suit: string; rank: string }) {
        this.send({ type: 'play_card', card })
      }

      pass() {
        this.send({ type: 'pass' })
      }

      selectContract(contract: string, trumpSuit?: string, calledAce?: string) {
        this.send({ type: 'select_contract', contract, trump_suit: trumpSuit, called_ace: calledAce })
      }

      getState() {
        this.send({ type: 'get_state' })
      }

      disconnect() {
        globalMessageCallback = null
      }
    }
  }
})

// Helper function to simulate WebSocket messages in tests
export function simulateWebSocketMessage(message: any) {
  if (globalMessageCallback) {
    globalMessageCallback(message)
  }
}

// Set up global WebSocket mock
if (typeof window !== 'undefined') {
  (window as any).WebSocket = MockWebSocket
}
(globalThis as any).WebSocket = MockWebSocket

describe('GameBoard', () => {
  beforeEach(() => {
    // Clear localStorage
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.clear()
      window.localStorage.setItem('token', createMockToken('testuser'))
    }
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.clear()
    }
  })

  it('should display loading state initially', async () => {
    // Set up room ID in URL
    window.history.pushState({}, '', `?room=test-room`)
    
    render(
      <BrowserRouter>
        <GameBoard />
      </BrowserRouter>
    )
    
    // Component should show loading state initially
    expect(screen.getByText(/Connecting to game/i)).toBeTruthy()
  })

  it('should display player names correctly', async () => {
    // Set up room ID in URL
    window.history.pushState({}, '', `?room=test-room-123`)
    
    render(
      <BrowserRouter>
        <GameBoard />
      </BrowserRouter>
    )
    
    // Wait for component to initialize
    await waitFor(() => {
      expect(screen.queryByText(/Connecting to game/i) || screen.queryByText(/Waiting for game/i)).toBeTruthy()
    }, { timeout: 500 })
    
    // Simulate receiving game state message
    const { simulateWebSocketMessage } = await import('./GameBoard.test')
    simulateWebSocketMessage({
      type: 'game_state',
      state: {
        game_id: 'test-game',
        players: ['player1', 'player2', 'player3', 'player4'],
        your_player_index: 0,
        your_hand: [],
        other_hands: [8, 8, 8],
        current_trick: [],
        current_player: 0,
        contract: null,
        trick_number: 0,
        round_complete: false,
        bidding_phase: true,
        current_bidder: 0,
        highest_bid: null,
        passes_in_a_row: 0
      }
    })
    
    // Wait for the game state to be displayed
    await waitFor(() => {
      // The component displays player names in player-seat divs
      // Check for any player name from the array
      const player1Text = screen.queryByText(/player1/i)
      const player2Text = screen.queryByText(/player2/i)
      expect(player1Text || player2Text).toBeTruthy()
    }, { timeout: 2000 })
  })
})

