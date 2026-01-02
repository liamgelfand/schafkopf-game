import { Link, Navigate } from 'react-router-dom'
import './Home.css'

function Home() {
  const token = localStorage.getItem('token')
  
  // Redirect to dashboard if logged in
  if (token) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <div className="home">
      <div className="home-container">
        <h1>Schafkopf</h1>
        <p className="subtitle">Traditional German Card Game</p>
        <div className="menu-buttons">
          <Link to="/tutorial" className="menu-button">
            Tutorial
          </Link>
          <Link to="/login" className="menu-button primary">
            Login / Register
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Home

