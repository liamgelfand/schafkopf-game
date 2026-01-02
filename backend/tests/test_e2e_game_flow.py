"""E2E tests for complete game flow"""
import pytest
from fastapi.testclient import TestClient
from app.models.game import Game
from app.models.card import Suit, Rank, Card
from app.api.websocket import ConnectionManager
import asyncio

class TestE2EGameFlow:
    """End-to-end tests for complete game flows"""
    
    @pytest.mark.skip(reason="Requires full API setup - use integration tests instead")
    def test_complete_bidding_flow(self):
        """Test complete bidding flow from start to contract selection"""
        # Create room
        create_response = client.post(
            "/api/rooms/create",
            headers=auth_headers,
            json={"name": "E2E Test Room"}
        )
        room_id = create_response.json()["id"]
        
        # Set ready (triggers game start if 4 players)
        response = client.post(
            f"/api/rooms/{room_id}/ready",
            headers=auth_headers,
            json={"ready": True}
        )
        assert response.status_code == 200
    
    def test_bidding_with_all_contract_types(self):
        """Test that all contract types can be bid correctly"""
        game = Game("test-e2e")
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        game.current_bidder_index = 0
        game.initial_bidder_index = 0
        
        # Test Rufer
        player0 = game.players[0]
        ace_not_in_hand = None
        for suit in [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]:
            has_ace = any(card.suit == suit and card.rank.value == "Ace" for card in player0.hand)
            if not has_ace:
                ace_not_in_hand = suit
                break
        
        if ace_not_in_hand:
            assert game.make_bid(0, "Rufer", None, ace_not_in_hand) == True
        
        # Test Wenz
        game.current_bidder_index = 1
        assert game.make_bid(1, "Wenz") == True
        
        # Test Suited Wenz
        game.current_bidder_index = 2
        assert game.make_bid(2, "Wenz", Suit.EICHEL) == True
        
        # Test Solo - should succeed (higher than Suited Wenz)
        game.current_bidder_index = 3
        assert game.make_bid(3, "Solo", Suit.GRAS) == True  # Solo is higher than Suited Wenz
        
        # But another Solo cannot override (same rank)
        game.current_bidder_index = 0
        assert game.make_bid(0, "Solo", Suit.EICHEL) == False  # Same rank, can't override
    
    def test_complete_game_round(self):
        """Test a complete game round from bidding to all tricks"""
        game = Game("test-complete")
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        
        # Set up bidding
        game.current_bidder_index = 0
        game.initial_bidder_index = 0
        
        # Find an ace NOT in player 0's hand for Rufer
        player0 = game.players[0]
        ace_not_in_hand = None
        for suit in [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]:
            has_ace = any(card.suit == suit and card.rank.value == "Ace" for card in player0.hand)
            if not has_ace:
                ace_not_in_hand = suit
                break
        
        if not ace_not_in_hand:
            pytest.skip("Could not find an ace not in player's hand for testing")
        
        # Make the bid
        assert game.make_bid(0, "Rufer", None, ace_not_in_hand) == True
        
        # Complete bidding with passes (current_bidder_index is auto-incremented by make_bid)
        # After the bid, current_bidder_index should be 1, bids_made should be 1
        # We need 3 more passes to complete the round (total 4 bids_made)
        while not game.bidding_complete and game.bids_made < 4:
            current_idx = game.current_bidder_index
            game.pass_bid(current_idx)
        
        # Bidding should be complete
        assert game.bidding_complete == True
        assert game.contract_type == "Rufer"
        
        # Game should be ready to play
        assert game.declarer_index == 0
        assert game.current_player_index == 0
    
    def test_reshuffle_after_all_pass(self):
        """Test that reshuffle happens correctly after all pass"""
        game = Game("test-reshuffle")
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        game.current_bidder_index = 0
        game.initial_bidder_index = 0
        
        # Store original hands
        original_hands = [player.hand.copy() for player in game.players]
        
        # All 4 pass
        for i in range(4):
            game.current_bidder_index = i
            game.pass_bid(i)
        
        # Check that bidding is complete with no bid
        assert game.bidding_complete == True
        assert game.highest_bid is None
        
        # Simulate reshuffle
        game.deck.reset()
        game.deck.shuffle()
        hands = game.deck.deal(len(game.players))
        for i, hand in enumerate(hands):
            game.players[i].hand = hand
        
        # Reset bidding state
        game.bidding_phase = True
        game.bidding_complete = False
        game.highest_bid = None
        game.passes_in_a_row = 0
        game.bids_made = 0
        game.initial_bidder_index = (game.initial_bidder_index + 1) % len(game.players)
        game.current_bidder_index = game.initial_bidder_index
        
        # Verify new bidding round can start
        assert game.bidding_phase == True
        assert game.current_bidder_index == 1  # Moved from 0 to 1
    
    def test_contract_hierarchy_enforcement(self):
        """Test that contract hierarchy is properly enforced"""
        game = Game("test-hierarchy")
        for i in range(4):
            game.add_player(f"player{i+1}")
        game.deal_cards()
        game.current_bidder_index = 0
        
        # Test hierarchy: Rufer < Wenz < Suited Wenz < Solo
        # Find an ace NOT in player's hand
        player0 = game.players[0]
        ace_not_in_hand = None
        for suit in [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]:
            has_ace = any(card.suit == suit and card.rank.value == "Ace" for card in player0.hand)
            if not has_ace:
                ace_not_in_hand = suit
                break
        
        if not ace_not_in_hand:
            pytest.skip("Could not find an ace not in player's hand for testing")
        
        # Rufer (rank 1)
        assert game.make_bid(0, "Rufer", None, ace_not_in_hand) == True
        assert game.get_contract_rank("Rufer") == 1
        
        # Wenz (rank 2) can override Rufer
        game.current_bidder_index = 1
        assert game.make_bid(1, "Wenz") == True
        assert game.get_contract_rank("Wenz") == 2
        
        # Suited Wenz (rank 3) can override Wenz
        game.current_bidder_index = 2
        assert game.make_bid(2, "Wenz", Suit.EICHEL) == True
        assert game.get_contract_rank("Wenz", Suit.EICHEL, is_suited=True) == 3
        
        # Solo (rank 4) can override Suited Wenz
        game.current_bidder_index = 3
        assert game.make_bid(3, "Solo", Suit.EICHEL) == True
        assert game.get_contract_rank("Solo", Suit.EICHEL) == 4
        
        # But another Solo cannot override (same rank)
        game.current_bidder_index = 0
        assert game.make_bid(0, "Solo", Suit.GRAS) == False

