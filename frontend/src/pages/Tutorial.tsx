import { Link } from 'react-router-dom'
import './Tutorial.css'

function Tutorial() {
  return (
    <div className="tutorial">
      <div className="tutorial-container">
        <h1>Schafkopf Tutorial</h1>

        <section className="tutorial-section">
          <h2>Overview</h2>
          <p>
            Schafkopf is a traditional German trick-taking card game played with 4 players
            using a 32-card deck. The goal is to score at least 61 out of 120 possible points
            through strategic card play.
          </p>
        </section>

        <section className="tutorial-section">
          <h2>The Deck</h2>
          <p>The game uses a 32-card deck with four suits:</p>
          <ul>
            <li><strong>Eichel</strong> (Acorns) ♠</li>
            <li><strong>Gras</strong> (Leaves) ♣</li>
            <li><strong>Herz</strong> (Hearts) ♥</li>
            <li><strong>Schellen</strong> (Bells) ♦</li>
          </ul>
          <p>Each suit contains: Ace, King, Ober, Unter, Ten, 9, 8, 7</p>
        </section>

        <section className="tutorial-section">
          <h2>Card Values</h2>
          <ul>
            <li><strong>Ace:</strong> 11 points</li>
            <li><strong>Ten:</strong> 10 points</li>
            <li><strong>King:</strong> 4 points</li>
            <li><strong>Ober:</strong> 3 points</li>
            <li><strong>Unter:</strong> 2 points</li>
            <li><strong>9, 8, 7:</strong> 0 points</li>
          </ul>
          <p>Total: 120 points per round</p>
        </section>

        <section className="tutorial-section">
          <h2>Contracts</h2>

          <div className="contract-explanation">
            <h3>Rufer (Calling Game)</h3>
            <p>
              The declarer calls an Ace they don't hold. The player holding that Ace becomes
              their partner. Together they play against the other two players.
            </p>
            <p><strong>Trumps:</strong> All Obers + Unters + all Hearts (14 trumps)</p>
          </div>

          <div className="contract-explanation">
            <h3>Wenz</h3>
            <p>
              The declarer plays solo against all three opponents. Only Unters are trumps.
            </p>
            <p><strong>Trumps:</strong> Only Unters (4 trumps)</p>
          </div>

          <div className="contract-explanation">
            <h3>Solo</h3>
            <p>
              The declarer plays solo and chooses a trump suit. All cards of that suit plus
              all Obers and Unters are trumps.
            </p>
            <p><strong>Trumps:</strong> Chosen suit + all Obers + all Unters</p>
          </div>
        </section>

        <section className="tutorial-section">
          <h2>Gameplay</h2>
          <ol>
            <li>Each player receives 8 cards</li>
            <li>Players bid for contracts (or play Rufer by default)</li>
            <li>Players take turns playing cards in tricks</li>
            <li>Must follow suit if possible</li>
            <li>Highest card of led suit (or highest trump) wins the trick</li>
            <li>After 8 tricks, points are calculated</li>
          </ol>
        </section>

        <section className="tutorial-section">
          <h2>Scoring</h2>
          <ul>
            <li><strong>Base Win:</strong> 61-90 points</li>
            <li><strong>Schneider:</strong> 91-120 points (double points)</li>
            <li><strong>Schwarz:</strong> All 8 tricks won (double points again)</li>
          </ul>
          <p>
            Contract values: Rufer = 1 point, Wenz = 2 points, Solo = 3 points
          </p>
        </section>

        <section className="tutorial-section">
          <h2>Trump Order</h2>
          <p>In Rufer and Solo contracts, trumps rank as follows (highest to lowest):</p>
          <ol>
            <li>Herz Ober (highest)</li>
            <li>Eichel Ober</li>
            <li>Gras Ober</li>
            <li>Schellen Ober</li>
            <li>Herz Unter</li>
            <li>Eichel Unter</li>
            <li>Gras Unter</li>
            <li>Schellen Unter</li>
            <li>Herz Ace, Ten, King, 9, 8, 7 (in Rufer only)</li>
          </ol>
        </section>

        <div className="tutorial-actions">
          <Link to="/game" className="tutorial-button primary">
            Play Now
          </Link>
          <Link to="/" className="tutorial-button">
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Tutorial
