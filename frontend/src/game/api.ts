// API client for backend communication
const API_BASE_URL = '/api'

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  }
}

export async function createGame(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/game/create`, {
    method: 'POST',
    headers: getAuthHeaders(),
  })
  if (!response.ok) throw new Error('Failed to create game')
  return response.json()
}

export async function makeMove(gameId: string, card: any): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/game/${gameId}/move`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ card }),
  })
  if (!response.ok) throw new Error('Failed to make move')
  return response.json()
}

export async function passTurn(gameId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/game/${gameId}/pass`, {
    method: 'POST',
    headers: getAuthHeaders(),
  })
  if (!response.ok) throw new Error('Failed to pass')
  return response.json()
}

export async function getGameState(gameId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/game/${gameId}/state`, {
    headers: getAuthHeaders(),
  })
  if (!response.ok) throw new Error('Failed to get game state')
  return response.json()
}

// Room management
export async function createRoom(name?: string, isPrivate?: boolean): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/rooms/create`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ name: name || 'Game Room', is_private: isPrivate || false }),
  })
  if (!response.ok) throw new Error('Failed to create room')
  return response.json()
}

export async function listRooms(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/rooms/list`, {
    headers: getAuthHeaders(),
  })
  if (!response.ok) throw new Error('Failed to list rooms')
  return response.json()
}

export async function joinRoom(roomId?: string, joinCode?: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/rooms/join`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ room_id: roomId, join_code: joinCode }),
  })
  if (!response.ok) throw new Error('Failed to join room')
  return response.json()
}

export async function leaveRoom(roomId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/rooms/${roomId}/leave`, {
    method: 'POST',
    headers: getAuthHeaders(),
  })
  if (!response.ok) throw new Error('Failed to leave room')
  return response.json()
}

export async function setReady(roomId: string, ready: boolean): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/rooms/${roomId}/ready`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ ready }),
  })
  if (!response.ok) throw new Error('Failed to set ready')
  return response.json()
}

export async function startGame(roomId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/rooms/${roomId}/start`, {
    method: 'POST',
    headers: getAuthHeaders(),
  })
  if (!response.ok) throw new Error('Failed to start game')
  return response.json()
}

export async function getRoom(roomId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/rooms/${roomId}`, {
    headers: getAuthHeaders(),
  })
  if (!response.ok) throw new Error('Failed to get room')
  return response.json()
}


