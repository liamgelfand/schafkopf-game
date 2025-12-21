from typing import List, Optional
from app.models.player import Player
from app.models.deck import Deck
from app.models.card import Card, Suit
from app.game_logic.tricks import determine_trick_winner, is_valid_play
from app.game_logic.contracts import RuferContract, WenzContract, SoloContract, Contract

class Game:
    """Main game state and logic"""
    
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.players: List[Player] = []
        self.deck = Deck()
        self.current_trick: List[Card] = []
        self.current_player_index: int = 0
        self.contract: Optional[Contract] = None
        self.contract_type: Optional[str] = None
        self.declarer_index: Optional[int] = None
        self.partner_index: Optional[int] = None
        self.trump_suit: Optional[Suit] = None
        self.round_number: int = 0
        self.trick_number: int = 0
        self.all_tricks: List[List[Card]] = []
        self.game_over: bool = False
    
    def add_player(self, name: str, is_ai: bool = False):
        """Add a player to the game"""
        player_id = len(self.players)
        player = Player(player_id, name, is_ai)
        self.players.append(player)
    
    def deal_cards(self):
        """Deal cards to all players"""
        self.deck.shuffle()
        hands = self.deck.deal(len(self.players))
        for i, hand in enumerate(hands):
            self.players[i].hand = hand
    
    def set_contract(self, contract_type: str, declarer_index: int, trump_suit: Optional[Suit] = None, called_ace_suit: Optional[Suit] = None):
        """Set the contract for the game"""
        self.declarer_index = declarer_index
        self.contract_type = contract_type
        
        if contract_type == "Rufer":
            if called_ace_suit is None:
                raise ValueError("Rufer contract requires called_ace_suit")
            self.contract = RuferContract(declarer_index, called_ace_suit)
            self.partner_index = self.contract.find_partner(self.players)
        elif contract_type == "Wenz":
            self.contract = WenzContract(declarer_index)
        elif contract_type == "Solo":
            if trump_suit is None:
                raise ValueError("Solo contract requires trump_suit")
            self.contract = SoloContract(declarer_index, trump_suit)
            self.trump_suit = trump_suit
        else:
            raise ValueError(f"Unknown contract type: {contract_type}")
    
    def play_card(self, player_index: int, card: Card) -> bool:
        """
        Play a card from a player's hand
        
        Returns:
            True if card was played successfully
        """
        player = self.players[player_index]
        
        # Validate the play
        led_suit = self.current_trick[0].suit if self.current_trick else None
        
        if not is_valid_play(card, player, led_suit, self.contract_type, self.trump_suit):
            return False
        
        # Remove card from hand and add to trick
        if not player.remove_card(card):
            return False
        
        self.current_trick.append(card)
        
        # Move to next player
        if len(self.current_trick) < 4:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
        
        return True
    
    def complete_trick(self) -> int:
        """
        Complete the current trick and determine the winner
        
        Returns:
            Index of the winning player
        """
        if len(self.current_trick) != 4:
            raise ValueError("Trick must have 4 cards")
        
        # Calculate starting player index (who led the trick)
        starting_player = (self.current_player_index - 3) % len(self.players)
        
        # Determine winner using game logic
        winning_player = determine_trick_winner(
            self.current_trick,
            self.players,
            starting_player,
            self.contract_type,
            self.trump_suit
        )
        
        # Add trick to winner's collection
        self.players[winning_player].add_trick(self.current_trick.copy())
        self.all_tricks.append(self.current_trick.copy())
        
        # Set next player
        self.current_player_index = winning_player
        self.current_trick = []
        self.trick_number += 1
        
        return winning_player
    
    def is_round_complete(self) -> bool:
        """Check if the current round is complete (all 8 tricks played)"""
        return self.trick_number >= 8
    
    def calculate_scores(self) -> dict:
        """Calculate final scores for the round"""
        from app.game_logic.scoring import calculate_round_score
        
        if self.contract is None:
            raise ValueError("Contract must be set before calculating scores")
        
        return calculate_round_score(self.contract, self.players, self.all_tricks)

