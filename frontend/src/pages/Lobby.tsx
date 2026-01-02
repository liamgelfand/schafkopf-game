import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createRoom, listRooms, joinRoom, setReady, startGame, getRoom, leaveRoom as leaveRoomAPI } from '../game/api'
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

interface CurrentUser {
  id: number
  username: string
  email: string
}

function Lobby() {
  const [rooms, setRooms] = useState<GameRoom[]>([])
  const [currentRoom, setCurrentRoom] = useState<GameRoom | null>(null)
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      navigate('/login')
      return
    }

    loadCurrentUser()
    loadRooms()
    
    // Check if we have a room ID in URL params
    const urlParams = new URLSearchParams(window.location.search)
    const roomId = urlParams.get('room')
    if (roomId && !currentRoom) {
      // Try to join or get the room
      joinRoomHandler(roomId).catch(err => {
        console.log('Room join result:', err)
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Separate effect for polling when in a room
  useEffect(() => {
    if (!currentRoom) return
    
    const interval = setInterval(() => {
      refreshRoom()
    }, 2000)
    
    return () => clearInterval(interval)
  }, [currentRoom?.id]) // Only depend on room ID, not the whole object

  // Auto-navigate to game when it starts
  useEffect(() => {
    if (currentRoom && currentRoom.status === 'in_progress') {
      navigate(`/game?room=${currentRoom.id}`)
    }
  }, [currentRoom?.status, currentRoom?.id, navigate])

  const loadCurrentUser = async () => {
    const token = localStorage.getItem('token')
    if (!token) return

    try {
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const userData = await response.json()
        setCurrentUser({
          id: userData.id,
          username: userData.username,
          email: userData.email
        })
      }
    } catch (err) {
      console.error('Failed to load current user:', err)
    }
  }

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
      
      // If room was deleted or doesn't exist, clear local state
      if (!room) {
        setCurrentRoom(null)
        await loadRooms()
        return
      }
      
      setCurrentRoom(room)
      
      // If game started, navigate to game
      if (room.status === 'in_progress') {
        navigate(`/game?room=${room.id}`)
      }
    } catch (err: any) {
      // If room was deleted, clear local state
      if (err.message?.includes('404') || err.message?.includes('not found')) {
        setCurrentRoom(null)
        await loadRooms()
      } else {
        console.error('Failed to refresh room:', err)
      }
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
      // Refresh room state after joining
      setTimeout(() => refreshRoom(), 500)
    } catch (err: any) {
      if (err.message?.includes('already')) {
        // If already in room, just fetch the room state
        const room = await getRoom(roomId)
        setCurrentRoom(room)
      } else {
        setError(err.message || 'Failed to join room')
      }
    } finally {
      setLoading(false)
    }
  }

  const toggleReady = async () => {
    if (!currentRoom || !currentUser) return
    
    const isReady = currentRoom.players.find(p => p.user_id === currentUser.id)?.ready || false
    
    try {
      const room = await setReady(currentRoom.id, !isReady)
      setCurrentRoom(room)
      // Also refresh rooms list to update other players' views
      await loadRooms()
    } catch (err: any) {
      setError(err.message || 'Failed to set ready')
      // Refresh room state on error
      refreshRoom()
    }
  }

  const startGameHandler = async () => {
    if (!currentRoom) return
    
    setLoading(true)
    try {
      await startGame(currentRoom.id)
      navigate(`/game?room=${currentRoom.id}`)
    } catch (err: any) {
      setError(err.message || 'Failed to start game')
    } finally {
      setLoading(false)
    }
  }

  const leaveRoom = async () => {
    if (!currentRoom) return
    
    setLoading(true)
    try {
      await leaveRoomAPI(currentRoom.id)
      setCurrentRoom(null)
      await loadRooms()
    } catch (err: any) {
      // If room was deleted or doesn't exist, just clear local state
      if (err.message?.includes('404') || err.message?.includes('not found')) {
        setCurrentRoom(null)
        await loadRooms()
      } else {
        setError(err.message || 'Failed to leave room')
      }
    } finally {
      setLoading(false)
    }
  }

  if (currentRoom) {
    const isCreator = currentUser && currentRoom.creator_id === currentUser.id
    const currentPlayer = currentRoom.players.find(p => 
      currentUser && p.user_id === currentUser.id
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
                  {player.ready ? (
                    <span className="ready-badge">Ready</span>
                  ) : (
                    <span className="not-ready-badge">Not Ready</span>
                  )}
                </div>
              ))}
              {Array.from({ length: currentRoom.max_players - currentRoom.players.length }).map((_, i) => (
                <div key={`empty-${i}`} className="player-item empty">
                  Waiting for player...
                </div>
              ))}
            </div>
            {/* Debug info - remove in production */}
            {import.meta.env.MODE === 'development' && (
              <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
                Debug: Creator ID: {currentRoom.creator_id}, Your ID: {currentUser?.id}, 
                Is Creator: {isCreator ? 'Yes' : 'No'}, 
                All Ready: {allReady ? 'Yes' : 'No'} 
                ({currentRoom.players.filter(p => p.ready).length}/{currentRoom.players.length} ready)
              </div>
            )}
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
        
        <button onClick={createRoomHandler} className="create-room-button" disabled={loading}>
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

