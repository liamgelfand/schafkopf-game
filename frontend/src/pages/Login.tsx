import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import './Login.css'

// Use same backend base URL logic as API client
const API_BASE_URL = import.meta.env.VITE_BACKEND_HTTP_URL
  ? `${import.meta.env.VITE_BACKEND_HTTP_URL}/api`
  : '/api'

function Login() {
  const { t } = useTranslation()
  const [isLogin, setIsLogin] = useState(true)
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const url = isLogin
        ? `${API_BASE_URL}/auth/login`
        : `${API_BASE_URL}/auth/register`
      const body = isLogin
        ? new URLSearchParams({ username, password })
        : JSON.stringify({ username, email, password })

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': isLogin
            ? 'application/x-www-form-urlencoded'
            : 'application/json',
        },
        body,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || t('login.authenticationFailed'))
      }

      // Both login and register return token
      if (data.access_token) {
        localStorage.setItem('token', data.access_token)
        navigate('/')
      } else {
        throw new Error(t('login.noAccessToken'))
      }
    } catch (err: any) {
      setError(err.message || t('login.errorOccurred'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <h1>{t('login.title')}</h1>
        <div className="auth-tabs">
          <button
            className={isLogin ? 'active' : ''}
            onClick={() => setIsLogin(true)}
          >
            {t('login.login')}
          </button>
          <button
            className={!isLogin ? 'active' : ''}
            onClick={() => setIsLogin(false)}
          >
            {t('login.register')}
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="username">{t('login.username')}</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="email">{t('login.email')}</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password">{t('login.password')}</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete={isLogin ? 'current-password' : 'new-password'}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? t('common.loading') : isLogin ? t('login.login') : t('login.register')}
          </button>
        </form>

        <Link to="/" className="back-link">
          {t('common.backToHome')}
        </Link>
      </div>
    </div>
  )
}

export default Login


