import pytest
from app.models.game import Game
from app.models.card import Suit, Rank, Card
from app.models.deck import Deck

def test_game_initialization():
    """Test that a game can be initialized"""
    game = Game("test-game-1")
    assert game.game_id == "test-game-1"
    assert len(game.players) == 0
    assert game.bidding_phase == True
    assert game.bidding_complete == False

def test_add_players():
    """Test adding players to a game"""
    game = Game("test-game-2")
    game.add_player("player1")
    game.add_player("player2")
    game.add_player("player3")
    game.add_player("player4")
    
    assert len(game.players) == 4
    assert game.players[0].name == "player1"
    assert game.players[1].name == "player2"
    assert game.players[2].name == "player3"
    assert game.players[3].name == "player4"

def test_deal_cards():
    """Test that cards are dealt correctly"""
    game = Game("test-game-3")
    for i in range(4):
        game.add_player(f"player{i+1}")
    
    game.deal_cards()
    
    # Each player should have 8 cards
    for player in game.players:
        assert len(player.hand) == 8
    
    # Total cards dealt should be 32
    total_cards = sum(len(p.hand) for p in game.players)
    assert total_cards == 32

def test_bidding_phase():
    """Test bidding phase mechanics"""
    game = Game("test-game-4")
    for i in range(4):
        game.add_player(f"player{i+1}")
    game.deal_cards()
    
    # Set starting bidder
    game.current_bidder_index = 0
    game.bidding_phase = True
    game.bidding_complete = False
    
    # Player 0 makes a bid - find an ace NOT in player's hand
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
        assert game.highest_bid is not None
        assert game.highest_bid["contract_type"] == "Rufer"
        assert game.current_bidder_index == 1
    else:
        pytest.skip("Could not find an ace not in player's hand for testing")
    
    # Player 1 passes
    result = game.pass_bid(1)
    assert result == True
    assert game.passes_in_a_row == 1
    assert game.current_bidder_index == 2

def test_contract_ranking():
    """Test contract ranking system"""
    game = Game("test-game-5")
    
    # Rufer should rank lower than Wenz
    rufer_rank = game.get_contract_rank("Rufer")
    wenz_rank = game.get_contract_rank("Wenz")
    assert wenz_rank > rufer_rank
    
    # Suited Wenz should rank higher than regular Wenz
    suited_wenz_rank = game.get_contract_rank("Wenz", Suit.EICHEL, is_suited=True)
    assert suited_wenz_rank > wenz_rank
    
    # Solo contracts should all have equal rank (rank 4)
    solo_eichel = game.get_contract_rank("Solo", Suit.EICHEL)
    solo_gras = game.get_contract_rank("Solo", Suit.GRAS)
    solo_herz = game.get_contract_rank("Solo", Suit.HERZ)
    solo_schellen = game.get_contract_rank("Solo", Suit.SCHELLEN)
    
    # All Solo suits are equal value
    assert solo_eichel == solo_gras == solo_herz == solo_schellen == 4
    assert solo_eichel > suited_wenz_rank  # Solo is higher than Suited Wenz

def test_bid_validation():
    """Test that bids must be higher than current highest"""
    game = Game("test-game-6")
    for i in range(4):
        game.add_player(f"player{i+1}")
    game.deal_cards()
    game.current_bidder_index = 0
    
    # Make initial bid
    game.make_bid(0, "Wenz")
    
    # Try to bid lower (should fail)
    game.current_bidder_index = 1
    result = game.make_bid(1, "Rufer")
    assert result == False
    
    # Bid higher (should succeed)
    result = game.make_bid(1, "Solo", Suit.EICHEL)
    assert result == True

def test_bidding_completion():
    """Test that bidding ends after bid and 3 passes"""
    game = Game("test-game-7")
    for i in range(4):
        game.add_player(f"player{i+1}")
    game.deal_cards()
    game.current_bidder_index = 0
    
    # Player 0 makes a bid - find an ace not in hand
    player0 = game.players[0]
    ace_not_in_hand = None
    for suit in [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]:
        has_ace = any(card.suit == suit and card.rank.value == "Ace" for card in player0.hand)
        if not has_ace:
            ace_not_in_hand = suit
            break
    
    if ace_not_in_hand:
        game.make_bid(0, "Rufer", None, ace_not_in_hand)
        
        # Three passes should end bidding (after bid, 3 passes = complete)
        game.pass_bid(1)
        game.pass_bid(2)
        result = game.pass_bid(3)
        
        assert result == True
        assert game.bidding_complete == True
        assert game.bidding_phase == False
    else:
        pytest.skip("Could not find an ace not in player's hand for testing")

