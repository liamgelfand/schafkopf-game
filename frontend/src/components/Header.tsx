import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import LanguageSelector from './LanguageSelector'
import './Header.css'

function Header() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const token = localStorage.getItem('token')

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/')
    // Reload to clear any cached state
    window.location.reload()
  }

  const getCurrentUsername = () => {
    if (!token) return null
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return payload.sub || 'User'
    } catch {
      return null
    }
  }

  const username = getCurrentUsername()

  if (!token) {
    return null // Don't show header if not logged in
  }

  return (
    <header className="app-header">
      <div className="header-container">
        <Link to="/" className="header-logo">
          <h2>Schafkopf</h2>
        </Link>
        
        <div className="header-user">
          <LanguageSelector />
          <span className="header-username">{t('common.logout')}: <strong>{username}</strong></span>
          <button onClick={handleLogout} className="header-logout">
            {t('common.logout')}
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header

