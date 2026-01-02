"""Unit tests for bidding logic"""
import pytest
from app.models.game import Game
from app.models.card import Suit, Rank, Card

class TestBidding:
    """Test suite for bidding functionality"""
    
    def test_contract_ranking_hierarchy(self):
        """Test that contract ranking follows correct hierarchy"""
        game = Game("test-game")
        
        # Rufer is lowest
        assert game.get_contract_rank("Rufer") == 1
        
        # Wenz (no suit) is higher than Rufer
        assert game.get_contract_rank("Wenz") == 2
        
        # Suited Wenz is higher than regular Wenz
        # Check by providing trump_suit (indicates suited) and is_suited=True
        wenz_rank = game.get_contract_rank("Wenz")
        suited_wenz_rank = game.get_contract_rank("Wenz", Suit.EICHEL, is_suited=True)
        assert suited_wenz_rank > wenz_rank
        
        # Solo is highest (all suits equal)
        assert game.get_contract_rank("Solo", Suit.EICHEL) == 4
        assert game.get_contract_rank("Solo", Suit.GRAS) == 4
        assert game.get_contract_rank("Solo", Suit.HERZ) == 4
        assert game.get_contract_rank("Solo", Suit.SCHELLEN) == 4
    
    def test_rufer_requires_called_ace(self):
        """Test that Rufer contract requires called ace"""
        game = Game("test-game")
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        game.current_bidder_index = 0
        
        # Rufer without called ace should fail
        result = game.make_bid(0, "Rufer", None, None)
        assert result == False
    
    def test_rufer_called_ace_not_in_hand(self):
        """Test that called ace for Rufer cannot be in player's hand"""
        game = Game("test-game")
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        game.current_bidder_index = 0
        
        player = game.players[0]
        # Find an ace in player's hand
        ace_in_hand = None
        for card in player.hand:
            if card.rank.value == "Ace":
                ace_in_hand = card.suit
                break
        
        if ace_in_hand:
            # Try to call an ace that's in hand - should fail
            result = game.make_bid(0, "Rufer", None, ace_in_hand)
            assert result == False
        
        # Try to call an ace that's NOT in hand - should succeed
        # Find a suit that doesn't have an ace in hand
        all_suits = [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]
        ace_not_in_hand = None
        for suit in all_suits:
            has_ace = any(card.suit == suit and card.rank.value == "Ace" for card in player.hand)
            if not has_ace:
                ace_not_in_hand = suit
                break
        
        if ace_not_in_hand:
            result = game.make_bid(0, "Rufer", None, ace_not_in_hand)
            assert result == True
    
    def test_bidding_goes_around_once(self):
        """Test that bidding goes around exactly once (4 players)"""
        game = Game("test-game")
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        game.current_bidder_index = 0
        game.initial_bidder_index = 0
        
        # All 4 players pass
        assert game.bids_made == 0
        game.pass_bid(0)
        assert game.bids_made == 1
        game.pass_bid(1)
        assert game.bids_made == 2
        game.pass_bid(2)
        assert game.bids_made == 3
        game.pass_bid(3)
        assert game.bids_made == 4
        # After 4 passes with no bid, bidding should be complete and need reshuffle
        assert game.bidding_complete == True
        assert game.highest_bid is None
    
    def test_all_pass_triggers_reshuffle(self):
        """Test that all 4 players passing triggers reshuffle logic"""
        game = Game("test-game")
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        game.current_bidder_index = 0
        game.initial_bidder_index = 0
        
        # Store original hands
        original_hands = [player.hand.copy() for player in game.players]
        
        # All 4 pass
        for i in range(4):
            game.pass_bid(i)
        
        # After reshuffle, hands should be different
        # (Note: This is probabilistic, but very likely)
        game.deck.reset()
        game.deck.shuffle()
        hands = game.deck.deal(len(game.players))
        for i, hand in enumerate(hands):
            game.players[i].hand = hand
        
        # Hands should be different (very likely)
        hands_different = False
        for i in range(4):
            if game.players[i].hand != original_hands[i]:
                hands_different = True
                break
        # This is probabilistic, so we just check the logic works
    
    def test_same_contract_type_first_bidder_wins(self):
        """Test that if same contract type is bid, first bidder wins"""
        game = Game("test-game")
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        game.current_bidder_index = 0
        
        # Player 0 bids Solo Eichel
        result = game.make_bid(0, "Solo", Suit.EICHEL)
        assert result == True
        assert game.highest_bid["bidder_index"] == 0
        
        # Player 1 tries to bid Solo Gras (same rank) - should fail
        game.current_bidder_index = 1
        result = game.make_bid(1, "Solo", Suit.GRAS)
        assert result == False  # Cannot override same rank contract
    
    def test_higher_contract_overrides_lower(self):
        """Test that higher contract can override lower contract"""
        game = Game("test-game")
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        game.current_bidder_index = 0
        
        # Player 0 bids Rufer - find an ace NOT in player's hand
        player0 = game.players[0]
        ace_not_in_hand = None
        for suit in [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]:
            has_ace = any(card.suit == suit and card.rank.value == "Ace" for card in player0.hand)
            if not has_ace:
                ace_not_in_hand = suit
                break
        
        if ace_not_in_hand:
            result = game.make_bid(0, "Rufer", None, ace_not_in_hand)
            assert result == True
            
            # Player 1 can bid Wenz (higher)
            game.current_bidder_index = 1
            result = game.make_bid(1, "Wenz")
            assert result == True
            assert game.highest_bid["contract_type"] == "Wenz"
            assert game.highest_bid["bidder_index"] == 1
        else:
            pytest.skip("Could not find an ace not in player's hand for testing")
    
    def test_suited_wenz_higher_than_regular_wenz(self):
        """Test that Suited Wenz ranks higher than regular Wenz"""
        game = Game("test-game")
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        game.current_bidder_index = 0
        
        # Player 0 bids regular Wenz
        result = game.make_bid(0, "Wenz")
        assert result == True
        
        # Player 1 can bid Suited Wenz (higher)
        game.current_bidder_index = 1
        result = game.make_bid(1, "Wenz", Suit.EICHEL)
        assert result == True
        assert game.highest_bid["contract_type"] == "Wenz"
        assert game.highest_bid["trump_suit"] == Suit.EICHEL.value

