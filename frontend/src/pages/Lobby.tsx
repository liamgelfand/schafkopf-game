import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { createRoom, listRooms, joinRoom, joinRoomByCode, getRoom, leaveRoom as leaveRoomAPI } from '../game/api'
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
  room_code?: string
}

interface CurrentUser {
  id: number
  username: string
  email: string
}

function Lobby() {
  const { t } = useTranslation()
  const [rooms, setRooms] = useState<GameRoom[]>([])
  const [currentRoom, setCurrentRoom] = useState<GameRoom | null>(null)
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showJoinByCode, setShowJoinByCode] = useState(false)
  const [roomCodeInput, setRoomCodeInput] = useState('')
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
      const response = await fetch(
        (import.meta.env.VITE_BACKEND_HTTP_URL
          ? `${import.meta.env.VITE_BACKEND_HTTP_URL}/api/auth/me`
          : '/api/auth/me'),
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

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

  const createRoomHandler = async (isPrivate: boolean = false) => {
    setLoading(true)
    setError('')
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        navigate('/login')
        return
      }

      const newRoom = await createRoom('Game Room', isPrivate)
      setCurrentRoom(newRoom)
      await loadRooms()
      // Update URL to include room ID
      window.history.replaceState({}, '', `?room=${newRoom.id}`)
    } catch (err: any) {
      setError(err.message || t('errors.failedToCreateRoom'))
    } finally {
      setLoading(false)
    }
  }

  const joinByCodeHandler = async () => {
    if (!roomCodeInput.trim()) {
      setError(t('lobby.roomCodeRequired'))
      return
    }

    setLoading(true)
    setError('')
    try {
      const room = await joinRoomByCode(roomCodeInput.trim().toUpperCase())
      setCurrentRoom(room)
      await loadRooms()
      setShowJoinByCode(false)
      setRoomCodeInput('')
      // Update URL to include room ID
      window.history.replaceState({}, '', `?room=${room.id}`)
      setTimeout(() => refreshRoom(), 500)
    } catch (err: any) {
      setError(err.message || t('errors.failedToJoinRoom'))
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
        setError(err.message || t('errors.failedToJoinRoom'))
      }
    } finally {
      setLoading(false)
    }
  }

  // Ready logic removed: games auto-start when 4 players join

  // Manual start handler no longer used (games auto-start when room is full)

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
        setError(err.message || t('errors.failedToLeaveRoom'))
      }
    } finally {
      setLoading(false)
    }
  }

  if (currentRoom) {

    return (
      <div className="lobby-page">
        <div className="lobby-container">
          <h1>{t('lobby.gameRoom')}</h1>
          {error && <div className="error-message">{error}</div>}
          
          <div className="room-players">
            <h3>{t('common.players')} ({currentRoom.players.length}/{currentRoom.max_players})</h3>
            <div className="players-list">
              {currentRoom.players.map((player) => (
                <div key={player.user_id} className="player-item">
                  <span>{player.username}</span>
                </div>
              ))}
              {Array.from({ length: currentRoom.max_players - currentRoom.players.length }).map((_, i) => (
                <div key={`empty-${i}`} className="player-item empty">
                  {t('lobby.waitingForPlayer')}
                </div>
              ))}
            </div>
          </div>

          {currentRoom.is_private && currentRoom.room_code && (
            <div className="room-code-display">
              <h4>{t('lobby.roomCode')}</h4>
              <div className="room-code-box">
                <span className="room-code-text">{currentRoom.room_code}</span>
                <button 
                  className="copy-code-button"
                  onClick={() => {
                    navigator.clipboard.writeText(currentRoom.room_code || '')
                    alert(t('lobby.roomCodeCopied'))
                  }}
                >
                  {t('lobby.copyCode')}
                </button>
              </div>
              <p className="room-code-hint">{t('lobby.shareCodeHint')}</p>
            </div>
          )}

          <div className="room-actions">
            {/* No manual ready / start buttons – backend auto-starts when room is full */}
            <button onClick={leaveRoom} className="leave-button">
              {t('common.leaveRoom')}
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="lobby-page">
      <div className="lobby-container">
        <h1>{t('lobby.title')}</h1>
        <p>{t('lobby.joinOrCreate')}</p>
        
        <div className="room-creation-buttons">
          <button 
            onClick={() => createRoomHandler(false)} 
            className="create-room-button" 
            disabled={loading}
          >
            {loading ? t('common.creating') : t('lobby.createPublicRoom')}
          </button>
          <button 
            onClick={() => createRoomHandler(true)} 
            className="create-room-button private" 
            disabled={loading}
          >
            {loading ? t('common.creating') : t('lobby.createPrivateRoom')}
          </button>
          <button 
            onClick={() => setShowJoinByCode(!showJoinByCode)} 
            className="join-by-code-button" 
            disabled={loading}
          >
            {showJoinByCode ? t('lobby.cancel') : t('lobby.joinByCode')}
          </button>
        </div>

        {showJoinByCode && (
          <div className="join-by-code-section">
            <input
              type="text"
              placeholder={t('lobby.enterRoomCode')}
              value={roomCodeInput}
              onChange={(e) => setRoomCodeInput(e.target.value.toUpperCase())}
              className="room-code-input"
              maxLength={6}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  joinByCodeHandler()
                }
              }}
            />
            <button 
              onClick={joinByCodeHandler} 
              className="join-code-button"
              disabled={loading || !roomCodeInput.trim()}
            >
              {t('common.join')}
            </button>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}
        
        <div className="rooms-list">
          <h3>{t('lobby.availableRooms')}</h3>
          {rooms.length === 0 ? (
            <p className="no-rooms">{t('lobby.noRoomsAvailable')}</p>
          ) : (
            rooms.map((room) => (
              <div key={room.id} className="room-item">
                <div className="room-info">
                  <span className="room-name">{t('lobby.room')} {room.id.substring(0, 8)}</span>
                  <span className="room-players-count">
                    {room.players.length}/{room.max_players} {t('common.players')}
                  </span>
                </div>
                <button 
                  onClick={() => joinRoomHandler(room.id)} 
                  className="join-button"
                  disabled={room.players.length >= room.max_players || loading}
                >
                  {t('common.join')}
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

