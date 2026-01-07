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
            trump_suit: For Solo/Wenz contracts, the chosen trump suit (Suited Wenz)
        
        Returns:
            True if this card is a trump
        """
        if contract_type == "Wenz":
            # In Wenz: Only Unters are trumps
            # In Suited Wenz: Unters + all cards of the chosen suit
            if self.rank == Rank.UNTER:
                return True
            if trump_suit and self.suit == trump_suit:
                return True  # Suited Wenz - suit cards are also trumps
            return False
        
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
            trump_suit: For Solo/Wenz contracts, the chosen trump suit
        
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
            return self._compare_trump_ranks(other, contract_type, trump_suit)
        
        # Both are non-trumps - must follow suit
        if self.suit != led_suit or other.suit != led_suit:
            # Invalid comparison - should not happen in valid game
            return 0
        
        # Compare by rank order (non-trump)
        return self._compare_non_trump_ranks(other)
    
    def _compare_trump_ranks(self, other: 'Card', contract_type: str = "Rufer", trump_suit: Optional[Suit] = None) -> int:
        """
        Compare ranks when both cards are trumps.
        
        Contract-specific rules:
        - Wenz: Only Unters are trumps (Obers are NOT trumps)
        - Solo: Obers > Unters > Suit cards
        - Rufer: Obers > Unters > Hearts
        """
        # Contract-specific trump ranking:
        # - Wenz: Only Unters are trumps (Obers are NOT trumps)
        # - Solo: Obers > Unters > Suit cards
        # - Rufer: Obers > Unters > Hearts
        
        if contract_type == "Wenz":
            # In Wenz, Obers are NOT trumps, so if we're comparing trumps,
            # both must be Unters (or suit cards in Suited Wenz)
            # Unters beat suit cards
            if self.rank == Rank.UNTER and other.rank != Rank.UNTER:
                return 1  # Unter beats suit card
            if self.rank != Rank.UNTER and other.rank == Rank.UNTER:
                return -1  # Suit card loses to Unter
            # Both are Unters or both are suit cards - handled below
        else:
            # For Solo and Rufer: Obers > Unters
            # Obers are highest - beat Unters and suit cards
            if self.rank == Rank.OBER and other.rank != Rank.OBER:
                return 1
            if self.rank != Rank.OBER and other.rank == Rank.OBER:
                return -1
        
        # If both are Obers, compare by suit order
        # Order: Eichel > Gras > Herz > Schellen
        if self.rank == Rank.OBER and other.rank == Rank.OBER:
            ober_order = [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]
            self_idx = ober_order.index(self.suit)
            other_idx = ober_order.index(other.suit)
            if self_idx < other_idx:
                return 1
            if self_idx > other_idx:
                return -1
            return 0
        
        # Unters are next - beat suit cards but lose to Obers (in Solo/Rufer)
        # In Wenz, only Unters are trumps, so this comparison only happens between Unters
        if self.rank == Rank.UNTER and other.rank != Rank.UNTER:
            return 1
        if self.rank != Rank.UNTER and other.rank == Rank.UNTER:
            return -1
        
        # If both are Unters, compare by suit order
        # Order: Eichel > Gras > Herz > Schellen
        if self.rank == Rank.UNTER and other.rank == Rank.UNTER:
            unter_order = [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]
            self_idx = unter_order.index(self.suit)
            other_idx = unter_order.index(other.suit)
            if self_idx < other_idx:
                return 1
            if self_idx > other_idx:
                return -1
            return 0
        
        # Both are suit cards (non-Ober/Unter trumps)
        # This happens in:
        # - Rufer: Hearts (Ace, Ten, King, Nine, Eight, Seven - Ober/Unter already counted)
        # - Solo: Chosen suit (Ace, Ten, King, Nine, Eight, Seven - Ober/Unter already counted)
        # - Suited Wenz: Chosen suit (Ace, Ten, King, Ober, Nine, Eight, Seven - Ober IS in suit)
        # Compare by rank order: Ace > Ten > King > 9 > 8 > 7
        # Note: In Suited Wenz, Ober of the suit is included in suit cards
        suit_card_order = [Rank.ACE, Rank.TEN, Rank.KING, Rank.NINE, Rank.EIGHT, Rank.SEVEN]
        if contract_type == "Wenz" and trump_suit:
            # In Suited Wenz, Ober of the suit is a suit card (not a separate trump category)
            suit_card_order = [Rank.ACE, Rank.TEN, Rank.KING, Rank.OBER, Rank.NINE, Rank.EIGHT, Rank.SEVEN]
        
        if self.rank in suit_card_order and other.rank in suit_card_order:
            self_idx = suit_card_order.index(self.rank)
            other_idx = suit_card_order.index(other.rank)
            if self_idx < other_idx:
                return 1
            if self_idx > other_idx:
                return -1
            return 0
        
        # Fallback: should not happen if both are trumps
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


