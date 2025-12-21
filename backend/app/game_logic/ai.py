import random
from typing import List, Optional
from app.models.player import Player
from app.models.card import Card, Suit
from app.game_logic.tricks import get_valid_plays

def ai_choose_card(
    player: Player,
    led_suit: Optional[Suit],
    contract_type: str,
    trump_suit: Optional[Suit] = None
) -> Optional[Card]:
    """
    Basic AI: Choose a random valid card to play
    
    Args:
        player: The AI player
        led_suit: The suit that was led (None if leading)
        contract_type: Type of contract
        trump_suit: For Solo contracts, the chosen trump suit
    
    Returns:
        A card to play, or None if no valid plays
    """
    valid_plays = get_valid_plays(player, led_suit, contract_type, trump_suit)
    
    if not valid_plays:
        return None
    
    # For now, just return a random valid card
    return random.choice(valid_plays)

def ai_choose_contract(
    player: Player,
    available_contracts: List[str]
) -> Optional[str]:
    """
    Basic AI: Choose a contract to play
    
    Args:
        player: The AI player
        available_contracts: List of available contract types
    
    Returns:
        Contract type to play, or None to pass
    """
    # For now, randomly decide whether to play or pass
    if random.random() < 0.3:  # 30% chance to play
        if available_contracts:
            return random.choice(available_contracts)
    return None

def ai_choose_called_ace(player: Player) -> Optional[Suit]:
    """
    AI chooses which Ace to call in Rufer contract
    
    Args:
        player: The AI player (declarer)
    
    Returns:
        Suit of the Ace to call, or None
    """
    from app.models.card import Rank, Suit
    
    # Find an Ace the player doesn't have
    player_aces = {card.suit for card in player.hand if card.rank == Rank.ACE}
    all_suits = [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]
    available_aces = [suit for suit in all_suits if suit not in player_aces]
    
    if available_aces:
        return random.choice(available_aces)
    return None

def ai_choose_trump_suit(player: Player) -> Suit:
    """
    AI chooses trump suit for Solo contract
    
    Args:
        player: The AI player (declarer)
    
    Returns:
        Chosen trump suit
    """
    from app.models.card import Suit
    
    # Simple strategy: choose suit with most high cards
    suit_counts = {suit: 0 for suit in Suit}
    high_ranks = ['Ace', 'Ten', 'King']
    
    for card in player.hand:
        if card.rank.value in high_ranks:
            suit_counts[card.suit] += 1
    
    # Return suit with most high cards, or random if tie
    max_count = max(suit_counts.values())
    best_suits = [suit for suit, count in suit_counts.items() if count == max_count]
    return random.choice(best_suits)


