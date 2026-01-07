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
        # Bidding phase state
        self.bidding_phase: bool = True
        self.current_bidder_index: int = 0
        self.highest_bid: Optional[dict] = None  # {contract_type, trump_suit, called_ace, bidder_index}
        self.passes_in_a_row: int = 0
        self.bidding_complete: bool = False
        self.bids_made: int = 0  # Track how many players have bid/passed (max 4, one round)
        self.initial_bidder_index: int = 0  # Track starting bidder for reshuffle logic
    
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
            # Wenz can be regular (no suit) or suited (with trump_suit)
            self.contract = WenzContract(declarer_index)
            if trump_suit:
                self.trump_suit = trump_suit  # Suited Wenz
        elif contract_type == "Solo":
            # Solo defaults to Hearts if no suit specified
            if trump_suit is None:
                trump_suit = Suit.HERZ
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
        led_card = self.current_trick[0] if self.current_trick else None
        
        if not is_valid_play(card, player, led_suit, self.contract_type, self.trump_suit, led_card):
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
    
    def get_contract_rank(self, contract_type: str, trump_suit: Optional[Suit] = None, is_suited: bool = False) -> int:
        """
        Get the rank/priority of a contract (higher = better)
        Contract hierarchy (lowest to highest):
        1. Rufer
        2. Wenz (Ober as trumps, no suit)
        3. Suited Wenz (Ober as trumps, with suit)
        4. Solo (all suits equal value, order matters if same type)
        """
        if contract_type == "Rufer":
            return 1
        elif contract_type == "Wenz":
            if is_suited:
                return 3  # Suited Wenz
            else:
                return 2  # Regular Wenz
        elif contract_type == "Solo":
            return 4  # All Solo suits are equal value
        return 0
    
    def make_bid(self, player_index: int, contract_type: str, trump_suit: Optional[Suit] = None, called_ace: Optional[Suit] = None) -> bool:
        """
        Make a bid during the bidding phase
        
        Contract types:
        - Rufer: Requires called_ace (must NOT be in player's hand)
        - Wenz: Ober as trumps, no suit
        - Suited Wenz: Ober as trumps, with trump_suit
        - Solo: Requires trump_suit (all suits equal value)
        """
        if not self.bidding_phase or self.bidding_complete:
            return False
        
        if player_index != self.current_bidder_index:
            return False
        
        # Validate contract requirements
        if contract_type == "Rufer":
            if called_ace is None:
                return False
            # Validate called ace is NOT in player's hand
            player = self.players[player_index]
            for card in player.hand:
                if card.rank.value == "Ace" and card.suit == called_ace:
                    return False  # Called ace cannot be in player's hand
        elif contract_type == "Wenz":
            # Wenz can be with or without suit (trump_suit indicates suited)
            pass
        elif contract_type == "Solo":
            # Solo can be bid without suit (defaults to Hearts)
            # trump_suit can be None, will default to Hearts in set_contract
            pass
        else:
            return False  # Unknown contract type
        
        # Determine if this is a suited Wenz
        is_suited_wenz = contract_type == "Wenz" and trump_suit is not None
        
        # Check if bid is higher than current highest
        bid_rank = self.get_contract_rank(contract_type, trump_suit, is_suited_wenz)
        if self.highest_bid:
            # Convert string back to Suit enum for comparison
            highest_trump = None
            if self.highest_bid.get("trump_suit"):
                try:
                    highest_trump = Suit(self.highest_bid["trump_suit"])
                except (ValueError, KeyError):
                    pass
            
            highest_contract = self.highest_bid["contract_type"]
            highest_is_suited = highest_contract == "Wenz" and highest_trump is not None
            highest_rank = self.get_contract_rank(
                highest_contract,
                highest_trump,
                highest_is_suited
            )
            
            # If same rank (e.g., both Solo), first bidder wins (order matters)
            if bid_rank < highest_rank:
                return False  # Bid is too low
            elif bid_rank == highest_rank:
                # Same contract type - first bidder wins, cannot override
                return False
        
        # Set as highest bid - convert Suit enums to strings for JSON serialization
        self.highest_bid = {
            "contract_type": contract_type,
            "trump_suit": trump_suit.value if trump_suit else None,
            "called_ace": called_ace.value if called_ace else None,
            "bidder_index": player_index
        }
        self.passes_in_a_row = 0
        self.bids_made += 1
        
        # Move to next player
        self.current_bidder_index = (self.current_bidder_index + 1) % len(self.players)
        
        # Check if we've gone around once (all 4 players have bid/passed)
        if self.bids_made >= 4:
            # Bidding round complete - end bidding phase
            self.end_bidding_phase()
        
        return True
    
    def pass_bid(self, player_index: int) -> bool:
        """
        Pass during the bidding phase
        Bidding goes around once (4 players). If all pass with no bid, reshuffle.
        """
        if not self.bidding_phase or self.bidding_complete:
            return False
        
        if player_index != self.current_bidder_index:
            return False
        
        self.passes_in_a_row += 1
        self.bids_made += 1
        
        # Move to next player
        self.current_bidder_index = (self.current_bidder_index + 1) % len(self.players)
        
        # Check if we've gone around once (all 4 players have bid/passed)
        if self.bids_made >= 4:
            if self.highest_bid:
                # Someone bid - end bidding phase
                self.end_bidding_phase()
            else:
                # All 4 players passed with no bid - need to reshuffle
                # This will be handled by the caller (rooms.py)
                self.bidding_complete = True
                self.bidding_phase = False
                # Signal that reshuffle is needed
                return True  # Return True to indicate all passed
        
        # If 3 passes in a row AND there's a highest bid, end bidding
        if self.passes_in_a_row >= 3 and self.highest_bid:
            self.end_bidding_phase()
        
        return True
    
    def end_bidding_phase(self):
        """End the bidding phase and set the contract"""
        self.bidding_phase = False
        self.bidding_complete = True
        
        if self.highest_bid:
            # Set the contract from the highest bid
            bid = self.highest_bid
            
            # Convert string back to Suit enum if present
            trump_suit_enum = None
            if bid.get("trump_suit"):
                try:
                    trump_suit_enum = Suit(bid["trump_suit"])
                except (ValueError, KeyError):
                    pass
            
            called_ace_enum = None
            if bid.get("called_ace"):
                try:
                    called_ace_enum = Suit(bid["called_ace"])
                except (ValueError, KeyError):
                    pass
            
            self.set_contract(
                bid["contract_type"],
                bid["bidder_index"],
                trump_suit_enum,
                called_ace_enum
            )
            # Set current player to declarer for first trick
            self.current_player_index = self.declarer_index
        else:
            # No one bid - this shouldn't happen in normal play, but handle it
            # For now, just set a default (this case needs proper handling)
            raise ValueError("No bids were made")

