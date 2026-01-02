import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import SettingsSidebar from '../components/SettingsSidebar'
import { listRooms, createRoom } from '../game/api'
import './Dashboard.css'

interface GameRoom {
  id: string
  creator_id: number
  players: Array<{ user_id: number; username: string; ready: boolean }>
  status: 'waiting' | 'starting' | 'in_progress'
  max_players: number
}

function Dashboard() {
  const [rooms, setRooms] = useState<GameRoom[]>([])
  const [showSettings, setShowSettings] = useState(false)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      navigate('/login')
      return
    }

    loadRooms()
    const interval = setInterval(loadRooms, 5000)
    return () => clearInterval(interval)
  }, [navigate])

  const loadRooms = async () => {
    try {
      const data = await listRooms()
      setRooms(data.rooms || [])
    } catch (err) {
      console.error('Failed to load rooms:', err)
    }
  }

  const handleCreateRoom = async () => {
    setLoading(true)
    try {
      const room = await createRoom('Game Room')
      // Join the room first, then navigate
      try {
        const { joinRoom } = await import('../game/api')
        await joinRoom(room.id)
      } catch (err) {
        // Already in room or other error, continue anyway
        console.log('Join room result:', err)
      }
      navigate(`/lobby?room=${room.id}`, { replace: true })
    } catch (err: any) {
      console.error('Failed to create room:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleJoinRoom = async (roomId: string) => {
    setLoading(true)
    try {
      const { joinRoom } = await import('../game/api')
      await joinRoom(roomId)
      navigate(`/lobby?room=${roomId}`, { replace: true })
    } catch (err: any) {
      console.error('Failed to join room:', err)
      // Try to navigate anyway in case we're already in the room
      navigate(`/lobby?room=${roomId}`, { replace: true })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Schafkopf Dashboard</h1>
        <button 
          className="settings-toggle"
          onClick={() => setShowSettings(!showSettings)}
          aria-label="Toggle settings"
        >
          ⚙️
        </button>
      </div>

      <div className="dashboard-content">
        <div className="dashboard-main">
          <section className="quick-actions">
            <h2>Quick Start</h2>
            <button 
              className="primary-button"
              onClick={handleCreateRoom}
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create New Game'}
            </button>
            <Link to="/lobby" className="secondary-button">
              Browse All Games
            </Link>
          </section>

          <section className="active-lobbies">
            <h2>Active Lobbies</h2>
            {rooms.length === 0 ? (
              <p className="no-rooms">No active lobbies. Create a game to get started!</p>
            ) : (
              <div className="rooms-list">
                {rooms.map(room => (
                  <div key={room.id} className="room-card">
                    <div className="room-info">
                      <h3>Game Room</h3>
                      <p className="room-status">
                        {room.players.length}/{room.max_players} players
                        {room.status === 'in_progress' && ' • In Progress'}
                      </p>
                      <div className="room-players">
                        {room.players.map(p => (
                          <span key={p.user_id} className="player-tag">
                            {p.username}
                          </span>
                        ))}
                      </div>
                    </div>
                    <button
                      className="join-button"
                      onClick={() => handleJoinRoom(room.id)}
                      disabled={room.status === 'in_progress' || room.players.length >= room.max_players}
                    >
                      {room.status === 'in_progress' ? 'In Progress' : 'Join'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="dashboard-stats">
            <h2>Quick Links</h2>
            <div className="quick-links">
              <Link to="/profile" className="link-card">
                <h3>Profile</h3>
                <p>View your profile and stats</p>
              </Link>
              <Link to="/stats" className="link-card">
                <h3>Statistics</h3>
                <p>View your game statistics</p>
              </Link>
              <Link to="/tutorial" className="link-card">
                <h3>Tutorial</h3>
                <p>Learn how to play</p>
              </Link>
            </div>
          </section>
        </div>
      </div>

      {showSettings && (
        <SettingsSidebar 
          isOpen={showSettings}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  )
}

export default Dashboard

