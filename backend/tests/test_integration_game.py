"""Integration tests for game logic"""
import pytest
from app.models.game import Game
from app.models.card import Suit, Rank, Card
from app.models.player import Player

class TestGameIntegration:
    """Integration tests combining multiple game components"""
    
    def test_full_bidding_to_play_flow(self):
        """Test complete flow from bidding to first card play"""
        game = Game("integration-test")
        
        # Setup
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        game.current_bidder_index = 0
        game.initial_bidder_index = 0
        
        # Bidding phase
        player0 = game.players[0]
        ace_not_in_hand = None
        for suit in [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]:
            has_ace = any(card.suit == suit and card.rank.value == "Ace" for card in player0.hand)
            if not has_ace:
                ace_not_in_hand = suit
                break
        
        if ace_not_in_hand:
            game.make_bid(0, "Rufer", None, ace_not_in_hand)
        
        # Complete bidding
        for i in range(1, 4):
            game.current_bidder_index = i
            game.pass_bid(i)
        
        # Verify contract is set
        assert game.bidding_complete == True
        assert game.contract_type == "Rufer"
        assert game.declarer_index == 0
        
        # Game should be ready to play
        assert game.current_player_index == 0
        assert len(game.players[0].hand) == 8
    
    def test_bidding_with_multiple_contracts(self):
        """Test bidding with multiple contract types in sequence"""
        game = Game("multi-contract")
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        game.current_bidder_index = 0
        
        # Sequence: Rufer -> Wenz -> Suited Wenz -> Solo
        # Find an ace NOT in player 0's hand
        player0 = game.players[0]
        ace_not_in_hand = None
        for suit in [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]:
            has_ace = any(card.suit == suit and card.rank.value == "Ace" for card in player0.hand)
            if not has_ace:
                ace_not_in_hand = suit
                break
        
        if ace_not_in_hand:
            # Player 0: Rufer
            assert game.make_bid(0, "Rufer", None, ace_not_in_hand) == True
            assert game.highest_bid["contract_type"] == "Rufer"
            
            # Player 1: Wenz (higher)
            game.current_bidder_index = 1
            assert game.make_bid(1, "Wenz") == True
            assert game.highest_bid["contract_type"] == "Wenz"
            
            # Player 2: Suited Wenz (higher)
            game.current_bidder_index = 2
            assert game.make_bid(2, "Wenz", Suit.EICHEL) == True
            assert game.highest_bid["contract_type"] == "Wenz"
            assert game.highest_bid["trump_suit"] == Suit.EICHEL.value
            
            # Player 3: Solo (highest)
            game.current_bidder_index = 3
            assert game.make_bid(3, "Solo", Suit.GRAS) == True
            assert game.highest_bid["contract_type"] == "Solo"
            assert game.highest_bid["trump_suit"] == Suit.GRAS.value
        else:
            pytest.skip("Could not find an ace not in player's hand for testing")
    
    def test_reshuffle_preserves_game_state(self):
        """Test that reshuffle preserves game structure"""
        game = Game("reshuffle-test")
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        game.current_bidder_index = 0
        game.initial_bidder_index = 0
        
        # All pass
        for i in range(4):
            game.current_bidder_index = i
            game.pass_bid(i)
        
        # Reshuffle
        game.deck.reset()
        game.deck.shuffle()
        hands = game.deck.deal(len(game.players))
        for i, hand in enumerate(hands):
            game.players[i].hand = hand
        
        # Verify game structure preserved
        assert len(game.players) == 4
        for player in game.players:
            assert len(player.hand) == 8

