import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createRoom, listRooms, joinRoom, setReady, startGame, getRoom } from '../game/api'
import './Lobby.css'

interface Player {
  user_id: number
  username: string
  ready: boolean
}

interface GameRoom {
  id: string
  creator_id: number
  players: Player[]
  max_players: number
  status: 'waiting' | 'starting' | 'in_progress'
  created_at: string
}

function Lobby() {
  const [rooms, setRooms] = useState<GameRoom[]>([])
  const [currentRoom, setCurrentRoom] = useState<GameRoom | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      navigate('/login')
      return
    }

    loadRooms()
    
    // Poll for room updates if in a room
    if (currentRoom) {
      const interval = setInterval(() => {
        refreshRoom()
      }, 2000)
      return () => clearInterval(interval)
    }
  }, [currentRoom])

  const loadRooms = async () => {
    try {
      const data = await listRooms()
      setRooms(data.rooms || [])
    } catch (err: any) {
      console.error('Failed to load rooms:', err)
      setError(err.message)
    }
  }

  const refreshRoom = async () => {
    if (!currentRoom) return
    try {
      const room = await getRoom(currentRoom.id)
      setCurrentRoom(room)
      
      // If game started, navigate to game
      if (room.status === 'in_progress') {
        navigate(`/game?room=${room.id}`)
      }
    } catch (err) {
      console.error('Failed to refresh room:', err)
    }
  }

  const createRoomHandler = async () => {
    setLoading(true)
    setError('')
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        navigate('/login')
        return
      }

      const newRoom = await createRoom()
      setCurrentRoom(newRoom)
      await loadRooms()
    } catch (err: any) {
      setError(err.message || 'Failed to create room')
    } finally {
      setLoading(false)
    }
  }

  const joinRoomHandler = async (roomId: string) => {
    setLoading(true)
    setError('')
    try {
      const room = await joinRoom(roomId)
      setCurrentRoom(room)
      await loadRooms()
    } catch (err: any) {
      setError(err.message || 'Failed to join room')
    } finally {
      setLoading(false)
    }
  }

  const toggleReady = async () => {
    if (!currentRoom) return
    
    const currentUser = JSON.parse(atob(localStorage.getItem('token')!.split('.')[1]))
    const isReady = currentRoom.players.find(p => p.user_id.toString() === currentUser.sub)?.ready || false
    
    try {
      const room = await setReady(currentRoom.id, !isReady)
      setCurrentRoom(room)
    } catch (err: any) {
      setError(err.message || 'Failed to set ready')
    }
  }

  const startGameHandler = async () => {
    if (!currentRoom) return
    
    setLoading(true)
    try {
      const result = await startGame(currentRoom.id)
      navigate(`/game?room=${currentRoom.id}`)
    } catch (err: any) {
      setError(err.message || 'Failed to start game')
    } finally {
      setLoading(false)
    }
  }

  const leaveRoom = async () => {
    if (!currentRoom) return
    
    try {
      // TODO: Call leave API
      setCurrentRoom(null)
      await loadRooms()
    } catch (err: any) {
      setError(err.message || 'Failed to leave room')
    }
  }

  if (currentRoom) {
    const currentUser = localStorage.getItem('token') 
      ? JSON.parse(atob(localStorage.getItem('token')!.split('.')[1]))
      : null
    const isCreator = currentUser && currentRoom.creator_id.toString() === currentUser.sub
    const currentPlayer = currentRoom.players.find(p => 
      currentUser && p.user_id.toString() === currentUser.sub
    )
    const allReady = currentRoom.players.length === currentRoom.max_players && 
                     currentRoom.players.every(p => p.ready)

    return (
      <div className="lobby-page">
        <div className="lobby-container">
          <h1>Game Room</h1>
          {error && <div className="error-message">{error}</div>}
          
          <div className="room-players">
            <h3>Players ({currentRoom.players.length}/{currentRoom.max_players})</h3>
            <div className="players-list">
              {currentRoom.players.map((player) => (
                <div key={player.user_id} className="player-item">
                  <span>{player.username}</span>
                  {player.ready && <span className="ready-badge">Ready</span>}
                </div>
              ))}
              {Array.from({ length: currentRoom.max_players - currentRoom.players.length }).map((_, i) => (
                <div key={`empty-${i}`} className="player-item empty">
                  Waiting for player...
                </div>
              ))}
            </div>
          </div>

          <div className="room-actions">
            {currentPlayer && (
              <button 
                onClick={toggleReady} 
                className={`ready-button ${currentPlayer.ready ? 'ready' : ''}`}
                disabled={loading}
              >
                {currentPlayer.ready ? 'Not Ready' : 'Ready'}
              </button>
            )}
            
            {isCreator && allReady && (
              <button 
                onClick={startGameHandler} 
                className="start-game-button"
                disabled={loading}
              >
                {loading ? 'Starting...' : 'Start Game'}
              </button>
            )}
            
            <button onClick={leaveRoom} className="leave-button">
              Leave Room
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="lobby-page">
      <div className="lobby-container">
        <h1>Game Lobby</h1>
        <p>Join or create a game room</p>
        
        <button onClick={createRoom} className="create-room-button" disabled={loading}>
          {loading ? 'Creating...' : 'Create New Room'}
        </button>

        {error && <div className="error-message">{error}</div>}
        
        <div className="rooms-list">
          <h3>Available Rooms</h3>
          {rooms.length === 0 ? (
            <p className="no-rooms">No rooms available. Create one to start!</p>
          ) : (
            rooms.map((room) => (
              <div key={room.id} className="room-item">
                <div className="room-info">
                  <span className="room-name">Room {room.id.substring(0, 8)}</span>
                  <span className="room-players-count">
                    {room.players.length}/{room.max_players} players
                  </span>
                </div>
                <button 
                  onClick={() => joinRoomHandler(room.id)} 
                  className="join-button"
                  disabled={room.players.length >= room.max_players || loading}
                >
                  Join
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default Lobby

