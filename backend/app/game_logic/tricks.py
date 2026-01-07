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
    trump_suit: Optional[Suit] = None,
    led_card: Optional[Card] = None
) -> List[Card]:
    """
    Get all valid cards a player can play
    
    Args:
        player: The player making the play
        led_suit: The suit that was led (None if leading)
        contract_type: Type of contract
        trump_suit: For Solo/Wenz contracts, the chosen trump suit
        led_card: The card that was led (to check if it's trump)
    
    Returns:
        List of valid cards to play
    """
    if led_suit is None:
        # Leading - can play any card
        return player.hand.copy()
    
    # Check if the led card is a trump
    led_is_trump = False
    if led_card:
        led_is_trump = led_card.is_trump(contract_type, trump_suit)
    
    if led_is_trump:
        # If a trump was led, must follow trump if possible
        trumps = [c for c in player.hand if c.is_trump(contract_type, trump_suit)]
        if trumps:
            return trumps
        # No trumps - can play any card
        return player.hand.copy()
    else:
        # Non-trump was led - must follow suit if possible
        cards_of_led_suit = [c for c in player.hand if c.suit == led_suit and not c.is_trump(contract_type, trump_suit)]
        if cards_of_led_suit:
            return cards_of_led_suit
        # Can't follow suit - can play any card (including trumps)
        return player.hand.copy()

def is_valid_play(
    card: Card,
    player: Player,
    led_suit: Optional[Suit],
    contract_type: str,
    trump_suit: Optional[Suit] = None,
    led_card: Optional[Card] = None
) -> bool:
    """
    Check if a card play is valid
    
    Args:
        card: The card to check
        player: The player making the play
        led_suit: The suit that was led (None if leading)
        contract_type: Type of contract
        trump_suit: For Solo/Wenz contracts, the chosen trump suit
        led_card: The card that was led (to check if it's trump)
    
    Returns:
        True if the play is valid
    """
    if card not in player.hand:
        return False
    
    valid_plays = get_valid_plays(player, led_suit, contract_type, trump_suit, led_card)
    return card in valid_plays

def get_invalid_play_reason(
    card: Card,
    player: Player,
    led_suit: Optional[Suit],
    contract_type: str,
    trump_suit: Optional[Suit] = None,
    led_card: Optional[Card] = None
) -> str:
    """
    Get the reason why a card play is invalid
    
    Args:
        card: The card to check
        player: The player making the play
        led_suit: The suit that was led (None if leading)
        contract_type: Type of contract
        trump_suit: For Solo/Wenz contracts, the chosen trump suit
        led_card: The card that was led (to check if it's trump)
    
    Returns:
        Reason string if invalid, empty string if valid
    """
    if card not in player.hand:
        return "You don't have this card in your hand."
    
    if led_suit is None:
        # Leading - any card is valid
        return ""
    
    # Check if the led card is a trump
    led_is_trump = False
    if led_card:
        led_is_trump = led_card.is_trump(contract_type, trump_suit)
    
    if led_is_trump:
        # If a trump was led, must follow trump if possible
        trumps = [c for c in player.hand if c.is_trump(contract_type, trump_suit)]
        if trumps:
            if not card.is_trump(contract_type, trump_suit):
                return f"You must follow trump. A trump card was led, and you have {len(trumps)} trump card(s) in your hand."
        # No trumps - any card is valid
        return ""
    else:
        # Non-trump was led - must follow suit if possible (but not trumps of that suit)
        cards_of_led_suit = [c for c in player.hand if c.suit == led_suit and not c.is_trump(contract_type, trump_suit)]
        if cards_of_led_suit:
            if card.suit != led_suit or card.is_trump(contract_type, trump_suit):
                return f"You must follow suit. The {led_suit.value} suit was led, and you have {len(cards_of_led_suit)} {led_suit.value} card(s) in your hand."
        # Can't follow suit - any card is valid
        return ""


