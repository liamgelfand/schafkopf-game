import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import './SettingsSidebar.css'

interface SettingsSidebarProps {
  isOpen: boolean
  onClose: () => void
}

function SettingsSidebar({ isOpen, onClose }: SettingsSidebarProps) {
  const { t, i18n } = useTranslation()
  const [preferences, setPreferences] = useState({
    theme: 'light',
    card_sort: 'suit',
    auto_sort_cards: true,
    sound_enabled: true,
    notifications_enabled: true,
    language: i18n.language || 'en'
  })

  useEffect(() => {
    loadPreferences()
  }, [])

  const loadPreferences = () => {
    const saved = localStorage.getItem('userPreferences')
    const savedLanguage = localStorage.getItem('language')
    if (saved) {
      try {
        const prefs = JSON.parse(saved)
        setPreferences(prefs)
        // Sync language with i18n
        if (prefs.language && prefs.language !== i18n.language) {
          i18n.changeLanguage(prefs.language)
        }
      } catch (err) {
        console.error('Failed to load preferences:', err)
      }
    } else if (savedLanguage) {
      // If no preferences but language is set, use it
      setPreferences(prev => ({ ...prev, language: savedLanguage }))
      i18n.changeLanguage(savedLanguage)
    }
  }

  const updatePreference = (key: string, value: any) => {
    const newPrefs = { ...preferences, [key]: value }
    setPreferences(newPrefs)
    localStorage.setItem('userPreferences', JSON.stringify(newPrefs))
    
    // If language changed, update i18n
    if (key === 'language') {
      i18n.changeLanguage(value)
      localStorage.setItem('language', value)
    }
  }

  if (!isOpen) return null

  return (
    <>
      <div className="settings-overlay" onClick={onClose} />
      <div className="settings-sidebar">
        <div className="settings-header">
          <h2>{t('settings.title')}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="settings-content">
          <section className="settings-section">
            <h3>{t('settings.appearance')}</h3>
            <div className="setting-item">
              <label>{t('settings.theme')}</label>
              <select
                value={preferences.theme}
                onChange={(e) => updatePreference('theme', e.target.value)}
              >
                <option value="light">{t('settings.light')}</option>
                <option value="dark">{t('settings.dark')}</option>
              </select>
            </div>
          </section>

          <section className="settings-section">
            <h3>{t('settings.gamePreferences')}</h3>
            <div className="setting-item">
              <label>{t('settings.cardSort')}</label>
              <select
                value={preferences.card_sort}
                onChange={(e) => updatePreference('card_sort', e.target.value)}
              >
                <option value="suit">{t('settings.bySuit')}</option>
                <option value="rank">{t('settings.byRank')}</option>
                <option value="trump">{t('settings.trumpsFirst')}</option>
              </select>
            </div>
            <div className="setting-item">
              <label>
                <input
                  type="checkbox"
                  checked={preferences.auto_sort_cards}
                  onChange={(e) => updatePreference('auto_sort_cards', e.target.checked)}
                />
                {t('settings.autoSortCards')}
              </label>
            </div>
          </section>

          <section className="settings-section">
            <h3>{t('settings.notifications')}</h3>
            <div className="setting-item">
              <label>
                <input
                  type="checkbox"
                  checked={preferences.sound_enabled}
                  onChange={(e) => updatePreference('sound_enabled', e.target.checked)}
                />
                {t('settings.soundEnabled')}
              </label>
            </div>
            <div className="setting-item">
              <label>
                <input
                  type="checkbox"
                  checked={preferences.notifications_enabled}
                  onChange={(e) => updatePreference('notifications_enabled', e.target.checked)}
                />
                {t('settings.notificationsEnabled')}
              </label>
            </div>
          </section>

          <section className="settings-section">
            <h3>{t('settings.language')}</h3>
            <div className="setting-item">
              <label>{t('settings.language')}</label>
              <select
                value={preferences.language}
                onChange={(e) => updatePreference('language', e.target.value)}
              >
                <option value="en">English</option>
                <option value="de">Deutsch</option>
                <option value="fr">Français</option>
                <option value="es">Español</option>
                <option value="zh">中文</option>
              </select>
            </div>
          </section>
        </div>
      </div>
    </>
  )
}

export default SettingsSidebar

