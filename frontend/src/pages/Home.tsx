import { Link, Navigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import './Home.css'

function Home() {
  const { t } = useTranslation()
  const token = localStorage.getItem('token')
  
  // Redirect to dashboard if logged in
  if (token) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <div className="home">
      <div className="home-container">
        <h1>{t('home.title')}</h1>
        <p className="subtitle">{t('home.subtitle')}</p>
        <p className="welcome-message">{t('home.welcomeMessage')}</p>
        <div className="menu-buttons">
          <Link to="/login" className="menu-button primary">
            {t('home.loginRegister')}
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Home

