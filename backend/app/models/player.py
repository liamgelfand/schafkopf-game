from typing import List
from app.models.card import Card

class Player:
    """Represents a player in the game"""
    
    def __init__(self, player_id: int, name: str, is_ai: bool = False):
        self.id = player_id
        self.name = name
        self.is_ai = is_ai
        self.hand: List[Card] = []
        self.tricks_won: List[List[Card]] = []
        self.points: int = 0
    
    def add_card(self, card: Card):
        """Add a card to the player's hand"""
        self.hand.append(card)
    
    def remove_card(self, card: Card) -> bool:
        """
        Remove a card from the player's hand
        
        Returns:
            True if card was removed, False if not found
        """
        try:
            self.hand.remove(card)
            return True
        except ValueError:
            return False
    
    def has_card(self, card: Card) -> bool:
        """Check if player has a specific card"""
        return card in self.hand
    
    def get_valid_plays(
        self,
        led_suit: 'Suit',
        contract_type: str,
        trump_suit: 'Suit' = None
    ) -> List[Card]:
        """
        Get all valid cards the player can play
        
        Args:
            led_suit: The suit that was led (None if leading)
            contract_type: Type of contract
            trump_suit: For Solo contracts, the chosen trump suit
        
        Returns:
            List of valid cards to play
        """
        if led_suit is None:
            # Leading - can play any card
            return self.hand.copy()
        
        # Must follow suit if possible
        cards_of_led_suit = [c for c in self.hand if c.suit == led_suit]
        
        if cards_of_led_suit:
            return cards_of_led_suit
        
        # Can't follow suit - can play any card
        return self.hand.copy()
    
    def add_trick(self, trick: List[Card]):
        """Add a won trick to the player's collection"""
        self.tricks_won.append(trick)
        # Calculate points from this trick
        for card in trick:
            self.points += card.value
    
    def reset_round(self):
        """Reset player state for a new round"""
        self.hand = []
        self.tricks_won = []
        self.points = 0


