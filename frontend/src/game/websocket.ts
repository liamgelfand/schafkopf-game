// WebSocket client for real-time game communication

export class GameWebSocket {
  private ws: WebSocket | null = null
  private gameId: string
  private onMessageCallback?: (message: any) => void

  constructor(gameId: string, userId: string) {
    this.gameId = gameId
    // userId stored for potential future use
    void userId
  }

  connect(onMessage: (message: any) => void) {
    this.onMessageCallback = onMessage
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const token = localStorage.getItem('token')
    const wsUrl = `${protocol}//${window.location.host}/ws/${this.gameId}?token=${encodeURIComponent(token || '')}`
    
    this.ws = new WebSocket(wsUrl)
    
    this.ws.onopen = () => {
      console.log('WebSocket connected, requesting initial game state')
      // Request initial game state after a small delay to ensure backend is ready
      setTimeout(() => {
        this.send({ type: 'get_state' })
      }, 100)
    }
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      if (this.onMessageCallback) {
        this.onMessageCallback(message)
      }
    }
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
    }
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }

  playCard(card: { suit: string; rank: string }) {
    this.send({
      type: 'play_card',
      card
    })
  }

  pass() {
    this.send({
      type: 'pass'
    })
  }

  selectContract(contract: string, trumpSuit?: string, calledAce?: string) {
    this.send({
      type: 'select_contract',
      contract,
      trump_suit: trumpSuit,
      called_ace: calledAce
    })
  }

  getState() {
    this.send({
      type: 'get_state'
    })
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

