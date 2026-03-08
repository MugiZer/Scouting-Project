import { useState } from 'react'

function App() {
  const [input, setInput] = useState('')
  const [status, setStatus] = useState('idle')
  const [message, setMessage] = useState('')
  const [scoutedData, setScoutedData] = useState([])

  const handleScout = async () => {
    if (!input.trim()) return

    setStatus('loading')
    setMessage('Fetching data...')
    setScoutedData([])

    try {
      const names = input.split(',').map(n => n.trim()).filter(n => n)
      const queryParams = names.map(n => `player_names=${encodeURIComponent(n)}`).join('&')

      const response = await fetch(`/players?${queryParams}`)

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const data = await response.json()

      if (data.scouted_players && data.scouted_players.length > 0) {
        setScoutedData(data.scouted_players)
        setStatus('success')
        setMessage(`${data.scouted_players.length} result(s) found`)
      } else {
        setStatus('error')
        setMessage('No results found')
      }

      setInput('')

    } catch (err) {
      console.error(err)
      setStatus('error')
      setMessage(err.message || 'Connection failed')
    }
  }

  const formatStatName = (key) => {
    return key
      .replace(/_/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, str => str.toUpperCase());
  }

  const formatStatValue = (value) => {
    if (typeof value === 'number') {
      return Number.isInteger(value) ? value : value.toFixed(2);
    }
    return value;
  }

  return (
    <div className="container">
      <div className="hero-section">
        <h1 className="hero-title">Data Scraper</h1>
        <div className="hero-subtitle">Player Intelligence</div>
      </div>

      <div className="scout-card">
        <div className="input-group">
          <label className="label">Search Players</label>
          <input
            className="input-field"
            placeholder="Hakimi, Bono, Ziyech..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleScout()}
          />
        </div>

        <button
          className="action-btn"
          onClick={handleScout}
          disabled={status === 'loading' || !input.trim()}
        >
          {status === 'loading' ? '> Scraping...' : '> Scrape'}
        </button>

        {status !== 'idle' && (
          <div className={`status-display status-${status}`}>
            {message}
          </div>
        )}
      </div>

      {scoutedData.length > 0 && (
        <div className="dashboard-grid">
          {scoutedData.map((player, idx) => (
            <div key={idx} className="player-card">
              <div className="player-header">
                <h2 className="player-name">{player.name}</h2>
                <div className="player-meta">
                  <span className="player-position">{player.position}</span>
                  <span className="player-league">{player.league}</span>
                </div>
              </div>

              <div className="stats-grid">
                {Object.entries(player.stats).map(([key, value]) => (
                  <div key={key} className="stat-item">
                    <div className="stat-value">{formatStatValue(value)}</div>
                    <div className="stat-label">{formatStatName(key)}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
export default App
