"""Unit tests for WebSocket handlers"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.api.websocket import ConnectionManager, handle_get_state, handle_select_contract, handle_pass, manager
from app.models.game import Game
from app.models.card import Suit

@pytest.fixture
def mock_manager():
    """Create a connection manager"""
    return ConnectionManager()

@pytest.fixture
def mock_game():
    """Create a mock game"""
    game = Game("test-game")
    for i in range(4):
        game.add_player(f"player{i+1}")
    game.deal_cards()
    game.current_bidder_index = 0
    game.initial_bidder_index = 0
    return game

@pytest.mark.asyncio
async def test_handle_get_state(mock_manager, mock_game):
    """Test getting game state via WebSocket"""
    game_id = "test-game"
    user_id = "player1"
    
    # Set up manager state
    mock_manager.games[game_id] = mock_game
    mock_manager.user_to_player_index[user_id] = 0
    mock_manager.active_connections[user_id] = AsyncMock()
    mock_manager.active_connections[user_id].send_json = AsyncMock()
    
    # Patch the global manager
    with patch('app.api.websocket.manager', mock_manager):
        await handle_get_state(game_id, user_id)
    
    # Verify message was sent
    assert mock_manager.active_connections[user_id].send_json.called

@pytest.mark.asyncio
async def test_handle_select_contract(mock_manager, mock_game):
    """Test selecting a contract via WebSocket"""
    game_id = "test-game"
    user_id = "player1"
    
    # Set up manager state
    mock_manager.games[game_id] = mock_game
    mock_manager.user_to_player_index[user_id] = 0
    mock_manager.active_connections[user_id] = AsyncMock()
    mock_manager.active_connections[user_id].send_json = AsyncMock()
    mock_manager.send_personal_message = AsyncMock()
    mock_manager.broadcast_to_game = AsyncMock()
    mock_game.current_bidder_index = 0  # Set current bidder
    mock_game.bidding_phase = True
    mock_game.bidding_complete = False
    
    # Create message
    message = {
        "contract": "Rufer",
        "called_ace": "Eichel"
    }
    
    # Find an ace not in player's hand
    player = mock_game.players[0]
    ace_not_in_hand = None
    for suit in [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]:
        has_ace = any(card.suit == suit and card.rank.value == "Ace" for card in player.hand)
        if not has_ace:
            ace_not_in_hand = suit.value
            break
    
    if ace_not_in_hand:
        message["called_ace"] = ace_not_in_hand
        # Patch the global manager
        with patch('app.api.websocket.manager', mock_manager):
            await handle_select_contract(game_id, user_id, message)
        # Should have made the bid
        assert mock_game.highest_bid is not None
    else:
        pytest.skip("Could not find an ace not in player's hand")

@pytest.mark.asyncio
async def test_handle_pass(mock_manager, mock_game):
    """Test passing via WebSocket"""
    game_id = "test-game"
    user_id = "player1"
    
    # Set up manager state
    mock_manager.games[game_id] = mock_game
    mock_manager.user_to_player_index[user_id] = 0
    mock_manager.active_connections[user_id] = AsyncMock()
    mock_manager.active_connections[user_id].send_json = AsyncMock()
    mock_manager.send_personal_message = AsyncMock()
    mock_manager.broadcast_to_game = AsyncMock()
    mock_game.current_bidder_index = 0  # Set current bidder
    mock_game.bidding_phase = True
    mock_game.bidding_complete = False
    
    message = {}
    # Patch the global manager
    with patch('app.api.websocket.manager', mock_manager):
        await handle_pass(game_id, user_id, message)
    
    # Should have incremented passes
    assert mock_game.passes_in_a_row >= 1

