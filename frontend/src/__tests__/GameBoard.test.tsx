import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, createMockToken } from './test-utils'
import GameBoard from '../components/GameBoard'

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
        // Simulate connection immediately
        // The component will show loading state until it receives a message
      }

      send(message: any) {
        // Mock send - can be used to verify calls
        // If get_state is requested, simulate a response
        if (message.type === 'get_state') {
          setTimeout(() => {
            if (globalMessageCallback) {
              globalMessageCallback({ type: 'game_not_ready' })
            }
          }, 50)
        }
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
    // Clear localStorage and set token before each test
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.clear()
      window.localStorage.setItem('token', createMockToken('testuser'))
    }
    // Reset global message callback
    globalMessageCallback = null
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.clear()
    }
    globalMessageCallback = null
  })

  it('should display loading state initially', async () => {
    // Set up room ID in URL
    window.history.pushState({}, '', `?room=test-room`)
    
    // Set token in localStorage before rendering
    window.localStorage.setItem('token', createMockToken('testuser'))
    
    render(<GameBoard />)
    
    // Component should show loading state initially
    // The component shows "Connecting to game..." when loading is true
    const loadingText = screen.getByText(/Connecting to game/i)
    expect(loadingText).toBeTruthy()
  })

  it('should display player names correctly', async () => {
    // Set up room ID in URL
    window.history.pushState({}, '', `?room=test-room-123`)
    
    // Set token in localStorage before rendering
    window.localStorage.setItem('token', createMockToken('testuser'))
    
    render(<GameBoard />)
    
    // Wait for component to initialize (should show loading, not error)
    await waitFor(() => {
      const errorText = screen.queryByText(/Not logged in/i)
      expect(errorText).toBeNull()
    }, { timeout: 1000 })
    
    // Simulate receiving game state message
    // Use a small delay to ensure the component is ready
    await new Promise(resolve => setTimeout(resolve, 150))
    
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
      const player3Text = screen.queryByText(/player3/i)
      const player4Text = screen.queryByText(/player4/i)
      expect(player1Text || player2Text || player3Text || player4Text).toBeTruthy()
    }, { timeout: 2000 })
  })
})

