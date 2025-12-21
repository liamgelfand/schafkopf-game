from enum import Enum
from typing import Optional

class Suit(Enum):
    EICHEL = "Eichel"  # Acorns
    GRAS = "Gras"      # Leaves
    HERZ = "Herz"      # Hearts
    SCHELLEN = "Schellen"  # Bells

class Rank(Enum):
    ACE = "Ace"
    KING = "King"
    OBER = "Ober"
    UNTER = "Unter"
    TEN = "Ten"
    NINE = "Nine"
    EIGHT = "Eight"
    SEVEN = "Seven"

class Card:
    """Represents a single card in the Schafkopf deck"""
    
    # Card point values
    POINT_VALUES = {
        Rank.ACE: 11,
        Rank.TEN: 10,
        Rank.KING: 4,
        Rank.OBER: 3,
        Rank.UNTER: 2,
        Rank.NINE: 0,
        Rank.EIGHT: 0,
        Rank.SEVEN: 0,
    }
    
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
        self.value = self.POINT_VALUES[rank]
    
    def __repr__(self):
        return f"Card({self.rank.value} of {self.suit.value})"
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank
    
    def __hash__(self):
        return hash((self.suit, self.rank))
    
    def is_trump(self, contract_type: str, trump_suit: Optional[Suit] = None) -> bool:
        """
        Determine if this card is a trump card based on contract type.
        
        Args:
            contract_type: Type of contract ('Rufer', 'Wenz', or 'Solo')
            trump_suit: For Solo contracts, the chosen trump suit
        
        Returns:
            True if this card is a trump
        """
        if contract_type == "Wenz":
            # Only Unters are trumps in Wenz
            return self.rank == Rank.UNTER
        
        if contract_type == "Solo":
            # In Solo: chosen suit + all Obers + all Unters
            if self.suit == trump_suit:
                return True
            return self.rank == Rank.OBER or self.rank == Rank.UNTER
        
        # Rufer (default): All Obers + Unters + all Hearts
        if self.rank == Rank.OBER or self.rank == Rank.UNTER:
            return True
        return self.suit == Suit.HERZ
    
    def compare_to(self, other: 'Card', led_suit: Suit, contract_type: str, trump_suit: Optional[Suit] = None) -> int:
        """
        Compare this card to another card in the context of a trick.
        
        Args:
            other: The card to compare against
            led_suit: The suit that was led in the trick
            contract_type: Type of contract
            trump_suit: For Solo contracts, the chosen trump suit
        
        Returns:
            -1 if this card is lower, 0 if equal, 1 if this card is higher
        """
        this_trump = self.is_trump(contract_type, trump_suit)
        other_trump = other.is_trump(contract_type, trump_suit)
        
        # Trumps always beat non-trumps
        if this_trump and not other_trump:
            return 1
        if not this_trump and other_trump:
            return -1
        
        # If both are trumps, compare by rank order
        if this_trump and other_trump:
            return self._compare_trump_ranks(other)
        
        # Both are non-trumps - must follow suit
        if self.suit != led_suit or other.suit != led_suit:
            # Invalid comparison - should not happen in valid game
            return 0
        
        # Compare by rank order (non-trump)
        return self._compare_non_trump_ranks(other)
    
    def _compare_trump_ranks(self, other: 'Card') -> int:
        """Compare ranks when both cards are trumps"""
        # Trump rank order (highest to lowest):
        # Herz Ober, Eichel Ober, Gras Ober, Schellen Ober,
        # Herz Unter, Eichel Unter, Gras Unter, Schellen Unter,
        # Then Hearts in order: Ace, Ten, King, 9, 8, 7
        
        # Obers are highest
        if self.rank == Rank.OBER and other.rank != Rank.OBER:
            return 1
        if self.rank != Rank.OBER and other.rank == Rank.OBER:
            return -1
        
        # If both are Obers, compare by suit
        if self.rank == Rank.OBER and other.rank == Rank.OBER:
            ober_order = [Suit.HERZ, Suit.EICHEL, Suit.GRAS, Suit.SCHELLEN]
            self_idx = ober_order.index(self.suit)
            other_idx = ober_order.index(other.suit)
            if self_idx < other_idx:
                return 1
            if self_idx > other_idx:
                return -1
            return 0
        
        # Unters are next
        if self.rank == Rank.UNTER and other.rank != Rank.UNTER:
            return 1
        if self.rank != Rank.UNTER and other.rank == Rank.UNTER:
            return -1
        
        # If both are Unters, compare by suit
        if self.rank == Rank.UNTER and other.rank == Rank.UNTER:
            unter_order = [Suit.HERZ, Suit.EICHEL, Suit.GRAS, Suit.SCHELLEN]
            self_idx = unter_order.index(self.suit)
            other_idx = unter_order.index(other.suit)
            if self_idx < other_idx:
                return 1
            if self_idx > other_idx:
                return -1
            return 0
        
        # Both are Hearts (non-Ober/Unter)
        # Order: Ace, Ten, King, 9, 8, 7
        heart_order = [Rank.ACE, Rank.TEN, Rank.KING, Rank.NINE, Rank.EIGHT, Rank.SEVEN]
        self_idx = heart_order.index(self.rank)
        other_idx = heart_order.index(other.rank)
        if self_idx < other_idx:
            return 1
        if self_idx > other_idx:
            return -1
        return 0
    
    def _compare_non_trump_ranks(self, other: 'Card') -> int:
        """Compare ranks when both cards are non-trumps of the same suit"""
        # Non-trump rank order (highest to lowest): Ace, Ten, King, Ober, Unter, 9, 8, 7
        rank_order = [
            Rank.ACE, Rank.TEN, Rank.KING, Rank.OBER,
            Rank.UNTER, Rank.NINE, Rank.EIGHT, Rank.SEVEN
        ]
        self_idx = rank_order.index(self.rank)
        other_idx = rank_order.index(other.rank)
        if self_idx < other_idx:
            return 1
        if self_idx > other_idx:
            return -1
        return 0


