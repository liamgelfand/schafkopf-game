from typing import List, Optional
from app.models.card import Card, Suit
from app.models.player import Player

def determine_trick_winner(
    trick: List[Card],
    players: List[Player],
    starting_player_index: int,
    contract_type: str,
    trump_suit: Optional[Suit] = None
) -> int:
    """
    Determine which player won the trick
    
    Args:
        trick: List of 4 cards played in order
        players: List of all players
        starting_player_index: Index of player who led the trick
        contract_type: Type of contract
        trump_suit: For Solo contracts, the chosen trump suit
    
    Returns:
        Index of the winning player
    """
    if len(trick) != 4:
        raise ValueError("Trick must contain exactly 4 cards")
    
    led_suit = trick[0].suit
    winning_card = trick[0]
    winning_index = 0
    
    for i in range(1, 4):
        card = trick[i]
        comparison = card.compare_to(winning_card, led_suit, contract_type, trump_suit)
        if comparison > 0:
            winning_card = card
            winning_index = i
    
    # Calculate actual player index
    player_index = (starting_player_index + winning_index) % len(players)
    return player_index

def get_valid_plays(
    player: Player,
    led_suit: Optional[Suit],
    contract_type: str,
    trump_suit: Optional[Suit] = None
) -> List[Card]:
    """
    Get all valid cards a player can play
    
    Args:
        player: The player making the play
        led_suit: The suit that was led (None if leading)
        contract_type: Type of contract
        trump_suit: For Solo contracts, the chosen trump suit
    
    Returns:
        List of valid cards to play
    """
    if led_suit is None:
        # Leading - can play any card
        return player.hand.copy()
    
    # Must follow suit if possible
    cards_of_led_suit = [c for c in player.hand if c.suit == led_suit]
    
    if cards_of_led_suit:
        return cards_of_led_suit
    
    # Can't follow suit - can play any card
    return player.hand.copy()

def is_valid_play(
    card: Card,
    player: Player,
    led_suit: Optional[Suit],
    contract_type: str,
    trump_suit: Optional[Suit] = None
) -> bool:
    """
    Check if a card play is valid
    
    Args:
        card: The card to check
        player: The player making the play
        led_suit: The suit that was led (None if leading)
        contract_type: Type of contract
        trump_suit: For Solo contracts, the chosen trump suit
    
    Returns:
        True if the play is valid
    """
    if card not in player.hand:
        return False
    
    valid_plays = get_valid_plays(player, led_suit, contract_type, trump_suit)
    return card in valid_plays


