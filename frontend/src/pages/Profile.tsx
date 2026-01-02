import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './Profile.css'

interface UserProfile {
  id: number
  username: string
  email: string
  avatar?: string
}

function Profile() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      navigate('/login')
      return
    }

    try {
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to load profile')
      }

      const data = await response.json()
      setProfile(data)
    } catch (err: any) {
      console.error('Failed to load profile:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/')
  }

  const getInitials = (username: string) => {
    return username.substring(0, 2).toUpperCase()
  }

  if (loading) {
    return (
      <div className="profile-page">
        <div className="profile-container">
          <p>Loading profile...</p>
        </div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="profile-page">
        <div className="profile-container">
          <p>Please log in to view your profile.</p>
          <Link to="/login" className="profile-button">Login</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="profile-page">
      <div className="profile-container">
        <h1>Profile</h1>

        <div className="profile-header">
          <div className="avatar-large">
            {profile.avatar ? (
              <img src={profile.avatar} alt={profile.username} />
            ) : (
              <div className="avatar-placeholder">
                {getInitials(profile.username)}
              </div>
            )}
          </div>
          <div className="profile-info">
            <h2>{profile.username}</h2>
            <p className="profile-email">{profile.email}</p>
          </div>
        </div>

        <div className="profile-sections">
          <section className="profile-section">
            <h3>Account Settings</h3>
            <div className="settings-list">
              <div className="setting-item">
                <label>Username</label>
                <input type="text" value={profile.username} disabled />
              </div>
              <div className="setting-item">
                <label>Email</label>
                <input type="email" value={profile.email} disabled />
              </div>
            </div>
          </section>

          <section className="profile-section">
            <h3>Preferences</h3>
            <div className="settings-list">
              <div className="setting-item">
                <label>Card Sort Preference</label>
                <select defaultValue="suit">
                  <option value="suit">By Suit</option>
                  <option value="rank">By Rank</option>
                  <option value="trump">Trumps First</option>
                </select>
              </div>
              <div className="setting-item">
                <label>Auto-sort Cards</label>
                <input type="checkbox" defaultChecked />
              </div>
            </div>
          </section>
        </div>

        <div className="profile-actions">
          <Link to="/stats" className="profile-button">
            View Statistics
          </Link>
          <button onClick={handleLogout} className="profile-button logout">
            Logout
          </button>
        </div>

        <Link to="/" className="back-link">
          Back to Home
        </Link>
      </div>
    </div>
  )
}

export default Profile

