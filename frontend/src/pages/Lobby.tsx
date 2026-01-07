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
  is_private?: boolean
  join_code?: string
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
  const [joinCode, setJoinCode] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      navigate('/login')
      return
    }

    // Load user first, then handle room
    loadCurrentUser().then(() => {
      loadRooms()
      
      // Check if we have a room ID in URL params
      const urlParams = new URLSearchParams(window.location.search)
      const roomId = urlParams.get('room')
      if (roomId && !currentRoom) {
        // Try to join or get the room
        joinRoomHandler(roomId).catch(err => {
          console.log('Room join result:', err)
          // If join fails, try to get the room directly
          getRoom(roomId).then(room => {
            if (room && room.id) {
              // Ensure players array exists
              if (!room.players) {
                room.players = []
              }
              setCurrentRoom(room)
            }
          }).catch(e => {
            console.error('Failed to get room:', e)
          })
        })
      }
    })
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
    if (!token) {
      navigate('/login')
      return Promise.resolve()
    }

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
      } else {
        // Token might be invalid
        localStorage.removeItem('token')
        navigate('/login')
      }
    } catch (err) {
      console.error('Failed to load current user:', err)
      // Don't navigate on error - might be network issue
    }
    return Promise.resolve()
  }

  const loadRooms = async () => {
    try {
      const data = await listRooms()
      setRooms(data.rooms || [])
    } catch (err: any) {
      console.error('Failed to load rooms:', err)
      setRooms([])
      // Don't set error here - it's not critical if room list fails
    }
  }

  const refreshRoom = async () => {
    if (!currentRoom || !currentRoom.id) return
    try {
      const room = await getRoom(currentRoom.id)
      
      // If room was deleted or doesn't exist, clear local state
      if (!room || !room.id) {
        setCurrentRoom(null)
        await loadRooms()
        return
      }
      
      // Ensure players array exists
      if (!room.players) {
        room.players = []
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

  const createRoomHandler = async (isPrivate: boolean = true) => {
    setLoading(true)
    setError('')
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        navigate('/login')
        return
      }

      const newRoom = await createRoom('Game Room', isPrivate)
      console.log('Room created:', newRoom)
      if (newRoom && newRoom.id) {
        // Ensure players array exists
        if (!newRoom.players) {
          newRoom.players = []
        }
        setCurrentRoom(newRoom)
        await loadRooms()
      } else {
        console.error('Invalid room response:', newRoom)
        setError('Invalid room response from server')
      }
    } catch (err: any) {
      console.error('Error creating room:', err)
      setError(err.message || 'Failed to create room')
    } finally {
      setLoading(false)
    }
  }

  const joinRoomHandler = async (roomId?: string, code?: string) => {
    setLoading(true)
    setError('')
    try {
      const room = await joinRoom(roomId, code)
      setCurrentRoom(room)
      await loadRooms()
      // Refresh room state after joining
      if (roomId) {
        setTimeout(() => refreshRoom(), 500)
      }
    } catch (err: any) {
      if (err.message?.includes('already')) {
        // If already in room, just fetch the room state
        if (roomId) {
          const room = await getRoom(roomId)
          setCurrentRoom(room)
        }
      } else {
        setError(err.message || 'Failed to join room')
      }
    } finally {
      setLoading(false)
    }
  }

  const joinByCodeHandler = async () => {
    if (!joinCode.trim()) {
      setError('Please enter a join code')
      return
    }
    await joinRoomHandler(undefined, joinCode.trim().toUpperCase())
    setJoinCode('')
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

  if (currentRoom && currentRoom.id) {
    // Safety check - ensure we have valid room data
    if (!currentRoom.players) {
      console.error('Room missing players array:', currentRoom)
      // Try to refresh the room
      if (currentRoom.id) {
        refreshRoom()
      }
      return (
        <div className="lobby-page">
          <div className="lobby-container">
            <h1>Loading Room...</h1>
            <p>Please wait while we load the room data.</p>
            <button onClick={() => { setCurrentRoom(null); setError(''); }}>Back to Lobby</button>
          </div>
        </div>
      )
    }
    
    // Wait for currentUser to load before showing room actions
    if (!currentUser) {
      return (
        <div className="lobby-page">
          <div className="lobby-container">
            <h1>Loading...</h1>
            <p>Please wait...</p>
          </div>
        </div>
      )
    }
    
    const isCreator = currentUser && currentRoom.creator_id === currentUser.id
    const players = currentRoom.players || []
    const currentPlayer = players.find(p => 
      currentUser && p.user_id === currentUser.id
    )
    const allReady = players.length === currentRoom.max_players && 
                     players.every(p => p.ready)

    return (
      <div className="lobby-page">
        <div className="lobby-container">
          <h1>Game Room</h1>
          {error && <div className="error-message">{error}</div>}
          
          {currentRoom.is_private && currentRoom.join_code && (
            <div className="join-code-display">
              <p>Share this code to invite others:</p>
              <div className="join-code">{currentRoom.join_code}</div>
              <button 
                onClick={() => navigator.clipboard.writeText(currentRoom.join_code || '')}
                className="copy-code-button"
              >
                Copy Code
              </button>
            </div>
          )}
          
          <div className="room-players">
            <h3>Players ({players.length}/{currentRoom.max_players})</h3>
            <div className="players-list">
              {players.map((player) => (
                <div key={player.user_id} className="player-item">
                  <span>{player.username}</span>
                  {player.ready ? (
                    <span className="ready-badge">Ready</span>
                  ) : (
                    <span className="not-ready-badge">Not Ready</span>
                  )}
                </div>
              ))}
              {Array.from({ length: currentRoom.max_players - players.length }).map((_, i) => (
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
                ({players.filter(p => p.ready).length}/{players.length} ready)
              </div>
            )}
          </div>

          <div className="room-actions">
            {currentPlayer && (
              <button 
                onClick={toggleReady} 
                className={`ready-button ${currentPlayer.ready ? 'ready' : 'not-ready'}`}
                disabled={loading}
              >
                {currentPlayer.ready ? 'Cancel' : 'Ready Up'}
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
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="lobby-sections">
          {/* Private Room Section */}
          <div className="private-room-section">
            <div className="section-header">
              <div className="section-icon">🔒</div>
              <div>
                <h2>Create Private Room</h2>
                <p className="section-description">Create a room with a shareable code</p>
              </div>
            </div>
            <button 
              onClick={() => createRoomHandler(true)} 
              className="create-private-button" 
              disabled={loading}
            >
              {loading ? (
                <span className="button-content">
                  <span className="spinner"></span>
                  Creating...
                </span>
              ) : (
                <span className="button-content">
                  <span className="button-icon">🔒</span>
                  Create Private Room
                </span>
              )}
            </button>
          </div>

          {/* Join by Code Section */}
          <div className="join-by-code-section">
            <div className="section-header">
              <div className="section-icon">🔑</div>
              <div>
                <h2>Join with Code</h2>
                <p className="section-description">Enter a code to join a private room</p>
              </div>
            </div>
            <div className="join-code-content">
              <div className="join-code-input-group">
                <input
                  type="text"
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                  placeholder="Enter 6-8 character code"
                  maxLength={8}
                  className="join-code-input-field"
                />
                <button 
                  onClick={joinByCodeHandler} 
                  className="join-code-submit-button" 
                  disabled={loading || !joinCode.trim()}
                >
                  {loading ? 'Joining...' : 'Join Room'}
                </button>
              </div>
              {joinCode && (
                <div className="code-preview">
                  <span className="code-preview-label">Code:</span>
                  <span className="code-preview-value">{joinCode}</span>
                </div>
              )}
            </div>
          </div>

          {/* Public Room Section */}
          <div className="public-room-section">
            <div className="section-header">
              <div className="section-icon">🌐</div>
              <div>
                <h2>Create Public Room</h2>
                <p className="section-description">Create a room that anyone can join</p>
              </div>
            </div>
            <button 
              onClick={() => createRoomHandler(false)} 
              className="create-public-button" 
              disabled={loading}
            >
              {loading ? (
                <span className="button-content">
                  <span className="spinner"></span>
                  Creating...
                </span>
              ) : (
                <span className="button-content">
                  <span className="button-icon">🌐</span>
                  Create Public Room
                </span>
              )}
            </button>
          </div>
        </div>

        <div className="rooms-list">
          <h3>Available Public Rooms</h3>
          {rooms.length === 0 ? (
            <p className="no-rooms">No public rooms available. Create one to start!</p>
          ) : (
            rooms.map((room) => (
              <div key={room.id} className="room-item">
                <div className="room-info">
                  <div className="room-header-row">
                    <span className="room-name">Game Room</span>
                    <span className={`room-type-badge ${room.is_private ? 'private' : 'public'}`}>
                      {room.is_private ? '🔒 Private' : '🌐 Public'}
                    </span>
                  </div>
                  <span className="room-players-count">
                    {(room.players || []).length}/{room.max_players} players
                    {room.status === 'in_progress' && ' • In Progress'}
                  </span>
                  {room.players && room.players.length > 0 && (
                    <div className="room-players-preview">
                      {room.players.slice(0, 3).map(p => (
                        <span key={p.user_id} className="player-preview-tag">
                          {p.username}
                        </span>
                      ))}
                      {room.players.length > 3 && (
                        <span className="player-preview-tag">+{room.players.length - 3}</span>
                      )}
                    </div>
                  )}
                </div>
                <button 
                  onClick={() => joinRoomHandler(room.id)} 
                  className="join-button"
                  disabled={(room.players || []).length >= room.max_players || loading || room.status === 'in_progress'}
                >
                  {room.status === 'in_progress' ? 'In Progress' : (room.players || []).length >= room.max_players ? 'Full' : 'Join'}
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

