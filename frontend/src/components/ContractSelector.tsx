import { ContractType } from '../game/types'
import './ContractSelector.css'

interface ContractSelectorProps {
  onSelect: (contract: ContractType, calledAce?: string, trumpSuit?: string) => void
  playerHand: any[]
  disabled?: boolean
}

function ContractSelector({ onSelect, playerHand, disabled = false }: ContractSelectorProps) {
  const handleRufer = () => {
    // For now, randomly select a called ace suit
    const suits = ['Eichel', 'Gras', 'Herz', 'Schellen']
    const playerAces = playerHand.filter(card => card.rank === 'Ace').map(card => card.suit)
    const availableAces = suits.filter(suit => !playerAces.includes(suit))
    const calledAce = availableAces[0] || suits[0]
    onSelect('Rufer', calledAce)
  }

  const handleWenz = () => {
    onSelect('Wenz')
  }

  const handleSolo = (trumpSuit: string) => {
    onSelect('Solo', undefined, trumpSuit)
  }

  return (
    <div className="contract-selector">
      <h3>Select Contract</h3>
      <div className="contract-buttons">
        <button onClick={handleRufer} disabled={disabled} className="contract-button">
          Rufer
        </button>
        <button onClick={handleWenz} disabled={disabled} className="contract-button">
          Wenz
        </button>
        <div className="solo-buttons">
          <span>Solo:</span>
          {['Eichel', 'Gras', 'Herz', 'Schellen'].map(suit => (
            <button
              key={suit}
              onClick={() => handleSolo(suit)}
              disabled={disabled}
              className="contract-button solo"
            >
              {suit}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ContractSelector


