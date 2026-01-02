import { useState, useEffect } from 'react'
import './SettingsSidebar.css'

interface SettingsSidebarProps {
  isOpen: boolean
  onClose: () => void
}

function SettingsSidebar({ isOpen, onClose }: SettingsSidebarProps) {
  const [preferences, setPreferences] = useState({
    theme: 'light',
    card_sort: 'suit',
    auto_sort_cards: true,
    sound_enabled: true,
    notifications_enabled: true,
    language: 'en'
  })

  useEffect(() => {
    loadPreferences()
  }, [])

  const loadPreferences = () => {
    const saved = localStorage.getItem('userPreferences')
    if (saved) {
      try {
        setPreferences(JSON.parse(saved))
      } catch (err) {
        console.error('Failed to load preferences:', err)
      }
    }
  }

  const updatePreference = (key: string, value: any) => {
    const newPrefs = { ...preferences, [key]: value }
    setPreferences(newPrefs)
    localStorage.setItem('userPreferences', JSON.stringify(newPrefs))
  }

  if (!isOpen) return null

  return (
    <>
      <div className="settings-overlay" onClick={onClose} />
      <div className="settings-sidebar">
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="settings-content">
          <section className="settings-section">
            <h3>Appearance</h3>
            <div className="setting-item">
              <label>Theme</label>
              <select
                value={preferences.theme}
                onChange={(e) => updatePreference('theme', e.target.value)}
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </div>
          </section>

          <section className="settings-section">
            <h3>Game Preferences</h3>
            <div className="setting-item">
              <label>Card Sort</label>
              <select
                value={preferences.card_sort}
                onChange={(e) => updatePreference('card_sort', e.target.value)}
              >
                <option value="suit">By Suit</option>
                <option value="rank">By Rank</option>
                <option value="trump">Trumps First</option>
              </select>
            </div>
            <div className="setting-item">
              <label>
                <input
                  type="checkbox"
                  checked={preferences.auto_sort_cards}
                  onChange={(e) => updatePreference('auto_sort_cards', e.target.checked)}
                />
                Auto-sort Cards
              </label>
            </div>
          </section>

          <section className="settings-section">
            <h3>Notifications</h3>
            <div className="setting-item">
              <label>
                <input
                  type="checkbox"
                  checked={preferences.sound_enabled}
                  onChange={(e) => updatePreference('sound_enabled', e.target.checked)}
                />
                Sound Enabled
              </label>
            </div>
            <div className="setting-item">
              <label>
                <input
                  type="checkbox"
                  checked={preferences.notifications_enabled}
                  onChange={(e) => updatePreference('notifications_enabled', e.target.checked)}
                />
                Notifications Enabled
              </label>
            </div>
          </section>

          <section className="settings-section">
            <h3>Language</h3>
            <div className="setting-item">
              <label>Language</label>
              <select
                value={preferences.language}
                onChange={(e) => updatePreference('language', e.target.value)}
              >
                <option value="en">English</option>
                <option value="de">Deutsch</option>
              </select>
            </div>
          </section>
        </div>
      </div>
    </>
  )
}

export default SettingsSidebar

