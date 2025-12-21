import { Link } from 'react-router-dom'
import './Home.css'

function Home() {
  return (
    <div className="home">
      <div className="home-container">
        <h1>Schafkopf</h1>
        <p className="subtitle">Traditional German Card Game</p>
        <div className="menu-buttons">
          {localStorage.getItem('token') ? (
            <>
              <Link to="/lobby" className="menu-button primary">
                Find Game
              </Link>
              <Link to="/tutorial" className="menu-button">
                Tutorial
              </Link>
              <Link to="/stats" className="menu-button">
                Statistics
              </Link>
              <Link to="/profile" className="menu-button">
                Profile
              </Link>
            </>
          ) : (
            <>
              <Link to="/tutorial" className="menu-button">
                Tutorial
              </Link>
              <Link to="/login" className="menu-button primary">
                Login / Register
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Home

