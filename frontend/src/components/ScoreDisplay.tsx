import './ScoreDisplay.css'

interface ScoreDisplayProps {
  scores: {
    declarer_points: number
    team_points: number
    opponents_points: number
    won: boolean
    schneider: boolean
    schwarz: boolean
  }
  contractType: string
}

function ScoreDisplay({ scores, contractType }: ScoreDisplayProps) {
  return (
    <div className="score-display">
      <h3>Round Results</h3>
      <div className="score-info">
        <div className="score-row">
          <span>Contract:</span>
          <span className="score-value">{contractType}</span>
        </div>
        <div className="score-row">
          <span>Team Points:</span>
          <span className="score-value">{scores.team_points}</span>
        </div>
        <div className="score-row">
          <span>Opponents Points:</span>
          <span className="score-value">{scores.opponents_points}</span>
        </div>
        <div className={`score-row result ${scores.won ? 'won' : 'lost'}`}>
          <span>Result:</span>
          <span className="score-value">{scores.won ? 'Won' : 'Lost'}</span>
        </div>
        {scores.schneider && (
          <div className="score-row special">
            <span>Schneider!</span>
          </div>
        )}
        {scores.schwarz && (
          <div className="score-row special">
            <span>Schwarz!</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default ScoreDisplay


