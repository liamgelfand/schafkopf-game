import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
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
  const { t } = useTranslation()
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

  const handleCreateRoom = async (isPrivate: boolean = false) => {
    setLoading(true)
    try {
      const room = await createRoom('Game Room', isPrivate)
      // Creator is automatically added to room, so just navigate
      navigate(`/lobby?room=${room.id}`, { replace: true })
    } catch (err: any) {
      console.error('Failed to create room:', err)
      alert(err.message || t('errors.failedToCreateRoom'))
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
        <h1>{t('dashboard.title')}</h1>
        <button 
          className="settings-toggle"
          onClick={() => setShowSettings(!showSettings)}
          aria-label={t('common.settings')}
        >
          ⚙️
        </button>
      </div>

      <div className="dashboard-content">
        <div className="dashboard-main">
          <section className="quick-actions">
            <h2>{t('dashboard.quickStart')}</h2>
            <button 
              className="primary-button"
              onClick={() => handleCreateRoom(false)}
              disabled={loading}
            >
              {loading ? t('common.creating') : t('dashboard.createNewGame')}
            </button>
            <button 
              className="primary-button"
              onClick={() => handleCreateRoom(true)}
              disabled={loading}
              style={{ marginTop: '0.5rem', background: 'linear-gradient(135deg, #f39c12 0%, #e67e22 100%)' }}
            >
              {loading ? t('common.creating') : t('lobby.createPrivateRoom')}
            </button>
            <Link to="/lobby" className="secondary-button">
              {t('dashboard.browseAllGames')}
            </Link>
          </section>

          <section className="active-lobbies">
            <h2>{t('dashboard.activeLobbies')}</h2>
            {rooms.length === 0 ? (
              <p className="no-rooms">{t('dashboard.noActiveLobbies')}</p>
            ) : (
              <div className="rooms-list">
                {rooms.map(room => (
                  <div key={room.id} className="room-card">
                    <div className="room-info">
                      <h3>{t('common.gameRoom')}</h3>
                      <p className="room-status">
                        {room.players.length}/{room.max_players} {t('common.players')}
                        {room.status === 'in_progress' && ` • ${t('common.inProgress')}`}
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
                      {room.status === 'in_progress' ? t('common.inProgress') : t('common.join')}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="dashboard-stats">
            <h2>{t('dashboard.quickLinks')}</h2>
            <div className="quick-links">
              <Link to="/profile" className="link-card">
                <h3>{t('common.profile')}</h3>
                <p>{t('dashboard.viewProfile')}</p>
              </Link>
              <Link to="/stats" className="link-card">
                <h3>{t('common.stats')}</h3>
                <p>{t('dashboard.viewStats')}</p>
              </Link>
              <Link to="/tutorial" className="link-card">
                <h3>{t('common.tutorial')}</h3>
                <p>{t('dashboard.learnToPlay')}</p>
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

