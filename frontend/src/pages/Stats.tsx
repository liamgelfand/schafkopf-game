import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './Stats.css'

interface GameHistory {
  id: string
  contractType: string
  won: boolean
  points: number
  schneider: boolean
  schwarz: boolean
  date: string
}

interface PlayerStats {
  gamesPlayed: number
  gamesWon: number
  winRate: number
  totalPoints: number
  schneiderCount: number
  schwarzCount: number
}

function Stats() {
  const [stats, setStats] = useState<PlayerStats | null>(null)
  const [history, setHistory] = useState<GameHistory[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      // Not logged in - show zeros
      setStats({
        gamesPlayed: 0,
        gamesWon: 0,
        winRate: 0,
        totalPoints: 0,
        schneiderCount: 0,
        schwarzCount: 0,
      })
      setHistory([])
      setLoading(false)
      return
    }

    try {
      // Load stats
      const statsResponse = await fetch('/api/stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats({
          gamesPlayed: statsData.gamesPlayed || 0,
          gamesWon: statsData.gamesWon || 0,
          winRate: statsData.winRate || 0,
          totalPoints: statsData.totalPoints || 0,
          schneiderCount: statsData.schneiderCount || 0,
          schwarzCount: statsData.schwarzCount || 0,
        })
      } else {
        // No stats yet - show zeros
        setStats({
          gamesPlayed: 0,
          gamesWon: 0,
          winRate: 0,
          totalPoints: 0,
          schneiderCount: 0,
          schwarzCount: 0,
        })
      }

      // Load history
      const historyResponse = await fetch('/api/history', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (historyResponse.ok) {
        const historyData = await historyResponse.json()
        setHistory(historyData || [])
      } else {
        setHistory([])
      }
    } catch (err) {
      console.error('Failed to load stats:', err)
      // Show zeros on error
      setStats({
        gamesPlayed: 0,
        gamesWon: 0,
        winRate: 0,
        totalPoints: 0,
        schneiderCount: 0,
        schwarzCount: 0,
      })
      setHistory([])
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="stats">
        <div className="stats-container">
          <p>Loading statistics...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="stats">
      <div className="stats-container">
        <h1>Statistics</h1>

        {stats && (
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Games Played</div>
              <div className="stat-value">{stats.gamesPlayed}</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Games Won</div>
              <div className="stat-value">{stats.gamesWon}</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Win Rate</div>
              <div className="stat-value">{stats.winRate}%</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Total Points</div>
              <div className="stat-value">{stats.totalPoints}</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Schneider</div>
              <div className="stat-value">{stats.schneiderCount}</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Schwarz</div>
              <div className="stat-value">{stats.schwarzCount}</div>
            </div>
          </div>
        )}

        <div className="history-section">
          <h2>Game History</h2>
          {history.length === 0 ? (
            <p className="no-history">No games played yet.</p>
          ) : (
            <div className="history-list">
              {history.map((game) => (
                <div key={game.id} className="history-item">
                  <div className="history-main">
                    <span className="history-contract">{game.contractType}</span>
                    <span className={`history-result ${game.won ? 'won' : 'lost'}`}>
                      {game.won ? 'Won' : 'Lost'}
                    </span>
                  </div>
                  <div className="history-details">
                    <span>{game.points} points</span>
                    {game.schneider && <span className="badge schneider">Schneider</span>}
                    {game.schwarz && <span className="badge schwarz">Schwarz</span>}
                    <span className="history-date">
                      {game.date ? new Date(game.date).toLocaleDateString() : ''}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <Link to="/" className="back-button">
          Back to Home
        </Link>
      </div>
    </div>
  )
}

export default Stats
