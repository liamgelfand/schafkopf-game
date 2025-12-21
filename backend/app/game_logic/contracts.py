from typing import List, Optional
from app.models.card import Suit
from app.models.player import Player

class Contract:
    """Base class for game contracts"""
    
    def __init__(self, contract_type: str, declarer_index: int):
        self.contract_type = contract_type
        self.declarer_index = declarer_index
        self.trump_suit: Optional[Suit] = None
    
    def get_trump_cards(self, all_cards: List) -> List:
        """Get all trump cards for this contract"""
        raise NotImplementedError
    
    def is_trump(self, card) -> bool:
        """Check if a card is a trump"""
        raise NotImplementedError

class RuferContract(Contract):
    """Rufer (Calling Game) contract"""
    
    def __init__(self, declarer_index: int, called_ace_suit: Suit):
        super().__init__("Rufer", declarer_index)
        self.called_ace_suit = called_ace_suit
        self.partner_index: Optional[int] = None
    
    def find_partner(self, players: List[Player]) -> Optional[int]:
        """
        Find the partner (player holding the called Ace)
        
        Returns:
            Index of partner player, or None if not found
        """
        from app.models.card import Rank
        
        for i, player in enumerate(players):
            if i == self.declarer_index:
                continue
            for card in player.hand:
                if card.suit == self.called_ace_suit and card.rank == Rank.ACE:
                    self.partner_index = i
                    return i
        return None
    
    def is_trump(self, card) -> bool:
        """In Rufer: All Obers + Unters + all Hearts"""
        from app.models.card import Rank
        
        if card.rank == Rank.OBER or card.rank == Rank.UNTER:
            return True
        return card.suit == Suit.HERZ

class WenzContract(Contract):
    """Wenz contract - only Unters are trumps"""
    
    def __init__(self, declarer_index: int):
        super().__init__("Wenz", declarer_index)
    
    def is_trump(self, card) -> bool:
        """In Wenz: Only Unters are trumps"""
        from app.models.card import Rank
        return card.rank == Rank.UNTER

class SoloContract(Contract):
    """Solo contract - declarer chooses trump suit"""
    
    def __init__(self, declarer_index: int, trump_suit: Suit):
        super().__init__("Solo", declarer_index)
        self.trump_suit = trump_suit
    
    def is_trump(self, card) -> bool:
        """In Solo: Chosen suit + all Obers + all Unters"""
        from app.models.card import Rank
        
        if card.suit == self.trump_suit:
            return True
        return card.rank == Rank.OBER or card.rank == Rank.UNTER


