from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import uuid
from app.models.game import Game
from app.models.player import Player
from app.models.card import Card, Suit, Rank

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # user_id -> WebSocket
        self.user_to_game: Dict[str, str] = {}  # user_id -> game_id
        self.game_players: Dict[str, List[str]] = {}  # game_id -> [user_ids]
        self.user_to_player_index: Dict[str, int] = {}  # user_id -> player_index in game
        self.games: Dict[str, Game] = {}
    
    def set_player_mapping(self, game_id: str, user_ids: List[str]):
        """Map user IDs to player indices"""
        for index, user_id in enumerate(user_ids):
            self.user_to_player_index[user_id] = index
    
    async def connect(self, websocket: WebSocket, game_id: str, user_id: str):
        # Note: websocket should already be accepted before calling this
        self.active_connections[user_id] = websocket
        self.user_to_game[user_id] = game_id
        
        if game_id not in self.game_players:
            self.game_players[game_id] = []
        if user_id not in self.game_players[game_id]:
            self.game_players[game_id].append(user_id)
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        game_id = self.user_to_game.get(user_id)
        if game_id and game_id in self.game_players:
            if user_id in self.game_players[game_id]:
                self.game_players[game_id].remove(user_id)
        
        if user_id in self.user_to_game:
            del self.user_to_game[user_id]
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
    
    async def broadcast_to_game(self, message: dict, game_id: str):
        if game_id in self.game_players:
            for user_id in self.game_players[game_id]:
                if user_id in self.active_connections:
                    await self.active_connections[user_id].send_json(message)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, game_id: str, user_id: str):
    """WebSocket endpoint for game communication"""
    await manager.connect(websocket, game_id, user_id)
    
    # Send initial game state
    await handle_get_state(game_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "play_card":
                await handle_play_card(game_id, user_id, message)
            elif message["type"] == "pass":
                await handle_pass(game_id, user_id, message)
            elif message["type"] == "select_contract":
                await handle_select_contract(game_id, user_id, message)
            elif message["type"] == "get_state":
                await handle_get_state(game_id, user_id)
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message.get('type')}"
                }, user_id)
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(user_id)

async def handle_play_card(game_id: str, user_id: str, message: dict):
    """Handle a card play from a player"""
    if game_id not in manager.games:
        await manager.send_personal_message({
            "type": "error",
            "message": "Game not found"
        }, user_id)
        return
    
    game = manager.games[game_id]
    
    # Get player index from mapping
    player_index = manager.user_to_player_index.get(user_id, 0)
    
    if player_index >= len(game.players):
        await manager.send_personal_message({
            "type": "error",
            "message": "Invalid player index"
        }, user_id)
        return
    
    # Convert card dict to Card object
    card_data = message.get("card", {})
    suit = Suit(card_data.get("suit"))
    rank = Rank(card_data.get("rank"))
    card = Card(suit, rank)
    
    # Play the card
    if game.play_card(player_index, card):
        # Check if trick is complete
        if len(game.current_trick) == 4:
            winner = game.complete_trick()
            await manager.broadcast_to_game({
                "type": "trick_complete",
                "winner": winner,
                "trick": [{"suit": c.suit.value, "rank": c.rank.value, "value": c.value} for c in game.all_tricks[-1]]
            }, game_id)
        
        # Broadcast updated game state
        await broadcast_game_state(game_id)
    else:
        await manager.send_personal_message({
            "type": "error",
            "message": "Invalid card play"
        }, user_id)

async def handle_pass(game_id: str, user_id: str, message: dict):
    """Handle a pass action"""
    if game_id not in manager.games:
        await manager.send_personal_message({
            "type": "error",
            "message": "Game not found"
        }, user_id)
        return
    
    game = manager.games[game_id]
    
    # Verify it's this player's turn
    player_index = manager.user_to_player_index.get(user_id, 0)
    if game.current_player_index != player_index:
        await manager.send_personal_message({
            "type": "error",
            "message": "Not your turn"
        }, user_id)
        return
    
    # Move to next player
    game.current_player_index = (game.current_player_index + 1) % len(game.players)
    
    await manager.broadcast_to_game({
        "type": "player_passed",
        "player_id": user_id,
        "current_player": game.current_player_index
    }, game_id)
    
    await broadcast_game_state(game_id)

async def handle_select_contract(game_id: str, user_id: str, message: dict):
    """Handle contract selection"""
    if game_id not in manager.games:
        await manager.send_personal_message({
            "type": "error",
            "message": "Game not found"
        }, user_id)
        return
    
    game = manager.games[game_id]
    contract_type = message.get("contract")
    trump_suit = message.get("trump_suit")
    called_ace = message.get("called_ace")
    
    # Get declarer index from mapping
    declarer_index = manager.user_to_player_index.get(user_id, 0)
    
    # Set contract
    trump_suit_enum = Suit(trump_suit) if trump_suit else None
    called_ace_enum = Suit(called_ace) if called_ace else None
    
    game.set_contract(contract_type, declarer_index, trump_suit_enum, called_ace_enum)
    
    await manager.broadcast_to_game({
        "type": "contract_selected",
        "contract": contract_type,
        "declarer": declarer_index
    }, game_id)
    
    await broadcast_game_state(game_id)

async def handle_get_state(game_id: str, user_id: str):
    """Send current game state to requesting player"""
    if game_id not in manager.games:
        await manager.send_personal_message({
            "type": "error",
            "message": "Game not found"
        }, user_id)
        return
    
    await send_game_state_to_user(game_id, user_id)

async def broadcast_game_state(game_id: str):
    """Broadcast game state to all players in the game"""
    if game_id not in manager.games:
        return
    
    game = manager.games[game_id]
    
    # Create game state for each player (only show their own hand)
    for i, user_id in enumerate(manager.game_players.get(game_id, [])):
        await send_game_state_to_user(game_id, user_id, player_index=i)

async def send_game_state_to_user(game_id: str, user_id: str, player_index: int = None):
    """Send game state to a specific user"""
    if game_id not in manager.games:
        return
    
    game = manager.games[game_id]
    
    # Determine player index from mapping
    if player_index is None:
        player_index = manager.user_to_player_index.get(user_id, 0)
    
    # Create state with player's hand visible
    player_hand = [
        {"suit": c.suit.value, "rank": c.rank.value, "value": c.value}
        for c in game.players[player_index].hand
    ]
    
    # Other players' hand sizes (but not cards)
    other_hands = [
        len(p.hand) if i != player_index else None
        for i, p in enumerate(game.players)
    ]
    
    state = {
        "game_id": game_id,
        "current_trick": [
            {"suit": c.suit.value, "rank": c.rank.value, "value": c.value}
            for c in game.current_trick
        ],
        "current_player": game.current_player_index,
        "your_hand": player_hand,
        "other_hands": other_hands,
        "contract": game.contract_type,
        "trick_number": game.trick_number,
        "round_complete": game.is_round_complete(),
        "players": [p.name for p in game.players]
    }
    
    await manager.send_personal_message({
        "type": "game_state",
        "state": state
    }, user_id)
