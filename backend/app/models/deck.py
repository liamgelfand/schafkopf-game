from typing import List
import random
from app.models.card import Card, Suit, Rank

class Deck:
    """Represents a 32-card Schafkopf deck"""
    
    def __init__(self):
        self.cards: List[Card] = []
        self._create_deck()
    
    def _create_deck(self):
        """Create a standard 32-card Schafkopf deck"""
        suits = [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]
        ranks = [
            Rank.ACE, Rank.KING, Rank.OBER, Rank.UNTER,
            Rank.TEN, Rank.NINE, Rank.EIGHT, Rank.SEVEN
        ]
        
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
    
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
    
    def deal(self, num_players: int = 4) -> List[List[Card]]:
        """
        Deal cards to players (8 cards each for 4 players)
        
        Args:
            num_players: Number of players (default 4)
        
        Returns:
            List of hands, one for each player
        """
        if len(self.cards) != 32:
            raise ValueError("Deck must have 32 cards")
        
        if num_players != 4:
            raise ValueError("Schafkopf requires exactly 4 players")
        
        hands = [[] for _ in range(num_players)]
        
        # Deal 8 cards to each player
        for i in range(8):
            for player in range(num_players):
                if self.cards:
                    hands[player].append(self.cards.pop(0))
        
        return hands
    
    def reset(self):
        """Reset the deck to a full 32-card deck"""
        self.cards = []
        self._create_deck()


