import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Game from './pages/Game'
import Tutorial from './pages/Tutorial'
import Stats from './pages/Stats'
import Login from './pages/Login'
import Profile from './pages/Profile'
import Lobby from './pages/Lobby'
import Header from './components/Header'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
          <Route path="/lobby" element={<Lobby />} />
          <Route path="/game" element={<Game />} />
          <Route path="/tutorial" element={<Tutorial />} />
          <Route path="/stats" element={<Stats />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App

