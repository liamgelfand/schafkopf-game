from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
import json
import uuid
from app.models.game import Game
from app.models.player import Player
from app.models.card import Card, Suit, Rank
from app.models.room import GameRoom
from app.game_logic.tricks import determine_trick_winner, is_valid_play, get_invalid_play_reason

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # user_id -> WebSocket
        self.user_to_game: Dict[str, str] = {}  # user_id -> game_id
        self.game_players: Dict[str, List[str]] = {}  # game_id -> [user_ids]
        self.user_to_player_index: Dict[str, int] = {}  # user_id -> player_index in game
        self.games: Dict[str, Game] = {}
        self.game_rooms: Dict[str, GameRoom] = {}  # game_id -> GameRoom (for user ID mapping)
    
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
        """Handle user disconnection and cleanup"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        game_id = self.user_to_game.get(user_id)
        if game_id:
            # Remove from game players list
            if game_id in self.game_players:
                if user_id in self.game_players[game_id]:
                    self.game_players[game_id].remove(user_id)
            
            # Clean up player index mapping
            if user_id in self.user_to_player_index:
                del self.user_to_player_index[user_id]
            
            # If game exists and has no active connections, mark for cleanup
            if game_id in self.games:
                active_count = len([uid for uid in self.game_players.get(game_id, []) if uid in self.active_connections])
                if active_count == 0:
                    print(f"No active connections for game {game_id}, marking for cleanup")
        
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
    print(f"WebSocket connection: user_id={user_id}, game_id={game_id}")
    await manager.connect(websocket, game_id, user_id)
    
    # Send initial game state if game exists
    # If game doesn't exist yet, wait for it to be created
    if game_id in manager.games:
        print(f"Sending initial game state to {user_id} (game exists)")
        await handle_get_state(game_id, user_id)
    else:
        print(f"Game {game_id} not found yet for {user_id}, will send state when game starts")
        # Send a message that game is not ready yet
        await manager.send_personal_message({
            "type": "game_not_ready",
            "message": "Game not started yet. Waiting for all players to be ready..."
        }, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "play_card":
                await handle_play_card(game_id, user_id, message)
            elif message["type"] == "pass":
                await handle_pass(game_id, user_id, message)
            elif message["type"] == "select_contract" or message["type"] == "bid":
                await handle_select_contract(game_id, user_id, message)
            elif message["type"] == "get_state":
                await handle_get_state(game_id, user_id)
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message.get('type')}"
                }, user_id)
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user: {user_id}")
        manager.disconnect(user_id)
        # Notify other players if in a game
        game_id = manager.user_to_game.get(user_id)
        if game_id:
            await manager.broadcast_to_game({
                "type": "player_disconnected",
                "user_id": user_id
            }, game_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
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
    
    # Validate it's the player's turn
    if player_index != game.current_player_index:
        print(f"ERROR: {user_id} (index {player_index}) tried to play out of turn. Current player: {game.current_player_index}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Not your turn. Current player: {game.current_player_index}, You are: {player_index}"
        }, user_id)
        return
    
    # Convert card dict to Card object
    card_data = message.get("card", {})
    suit = Suit(card_data.get("suit"))
    rank = Rank(card_data.get("rank"))
    card = Card(suit, rank)
    
    print(f"Card play: {user_id} (index {player_index}) playing {card.suit.value} {card.rank.value}")
    print(f"  Before play - current_player_index: {game.current_player_index}, trick size: {len(game.current_trick)}")
    
    # Validate the play before attempting it
    led_suit = game.current_trick[0].suit if game.current_trick else None
    if not is_valid_play(card, game.players[player_index], led_suit, game.contract_type, game.trump_suit):
        reason = get_invalid_play_reason(card, game.players[player_index], led_suit, game.contract_type, game.trump_suit)
        error_message = f"Cannot play this card. {reason}" if reason else "Cannot play this card. Invalid play."
        print(f"  Card play failed - {error_message}")
        await manager.send_personal_message({
            "type": "play_error",
            "message": error_message,
            "card": {"suit": card.suit.value, "rank": card.rank.value}
        }, user_id)
        # Send updated state so they can see valid plays
        await send_game_state_to_user(game_id, user_id, player_index)
        return
    
    # Play the card
    if game.play_card(player_index, card):
        print(f"  After play - current_player_index: {game.current_player_index}, trick size: {len(game.current_trick)}")
        
        # Check if trick is complete
        if len(game.current_trick) == 4:
            winner = game.complete_trick()
            print(f"  Trick complete - winner: {winner}, new current_player_index: {game.current_player_index}")
            await manager.broadcast_to_game({
                "type": "trick_complete",
                "winner": winner,
                "trick": [{"suit": c.suit.value, "rank": c.rank.value, "value": c.value} for c in game.all_tricks[-1]]
            }, game_id)
            
            # Check if round is complete (all 8 tricks played)
            if game.is_round_complete():
                await handle_round_complete(game_id)
        
        # Broadcast updated game state
        print(f"  Broadcasting game state - current_player_index: {game.current_player_index}")
        await broadcast_game_state(game_id)
    else:
        # This should rarely happen now since we validate first, but keep as fallback
        print(f"  Card play failed - game.play_card returned False")
        await manager.send_personal_message({
            "type": "play_error",
            "message": "Cannot play this card. The card may have already been played or is not in your hand.",
            "card": {"suit": card.suit.value, "rank": card.rank.value}
        }, user_id)
        # Send updated state so they can see valid plays
        await send_game_state_to_user(game_id, user_id, player_index)

async def handle_pass(game_id: str, user_id: str, message: dict):
    """Handle a pass action during bidding or gameplay"""
    if game_id not in manager.games:
        await manager.send_personal_message({
            "type": "error",
            "message": "Game not found"
        }, user_id)
        return
    
    game = manager.games[game_id]
    player_index = manager.user_to_player_index.get(user_id, 0)
    
    # Handle bidding phase pass
    if game.bidding_phase and not game.bidding_complete:
        if game.pass_bid(player_index):
            # Check if all 4 players passed with no bid (need to reshuffle)
            if game.bidding_complete and not game.highest_bid:
                # All players passed - reshuffle and redeal
                await manager.broadcast_to_game({
                    "type": "all_passed",
                    "message": "All players passed. Reshuffling cards..."
                }, game_id)
                
                # Reshuffle and redeal
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
                # Move to next starting bidder (clockwise)
                game.initial_bidder_index = (game.initial_bidder_index + 1) % len(game.players)
                game.current_bidder_index = game.initial_bidder_index
                game.current_player_index = game.current_bidder_index
                
                await manager.broadcast_to_game({
                    "type": "cards_reshuffled",
                    "new_starting_bidder": game.current_bidder_index,
                    "message": "Cards reshuffled. New bidding round starting."
                }, game_id)
                
                # Send updated game state after reshuffle
                await broadcast_game_state(game_id)
                return  # Exit early after reshuffle
            
            # Normal pass (not all passed)
            await manager.broadcast_to_game({
                "type": "bid_passed",
                "player_id": user_id,
                "player_index": player_index,
                "passes_in_a_row": game.passes_in_a_row,
                "bidding_complete": game.bidding_complete
            }, game_id)
            
            if game.bidding_complete and game.highest_bid:
                await manager.broadcast_to_game({
                    "type": "bidding_complete",
                    "contract": game.contract_type,
                    "declarer": game.declarer_index
                }, game_id)
            
            await broadcast_game_state(game_id)
        else:
            await manager.send_personal_message({
                "type": "error",
                "message": "Cannot pass (not your turn or invalid state)"
            }, user_id)
        return
    
    # Handle gameplay pass (if needed in future)
    await manager.send_personal_message({
        "type": "error",
        "message": "Cannot pass during gameplay"
    }, user_id)

async def handle_select_contract(game_id: str, user_id: str, message: dict):
    """Handle contract selection during bidding phase"""
    if game_id not in manager.games:
        await manager.send_personal_message({
            "type": "error",
            "message": "Game not found"
        }, user_id)
        return
    
    game = manager.games[game_id]
    
    # Must be in bidding phase
    if not game.bidding_phase or game.bidding_complete:
        await manager.send_personal_message({
            "type": "error",
            "message": "Not in bidding phase"
        }, user_id)
        return
    
    # Get player index - try multiple ways
    player_index = manager.user_to_player_index.get(user_id)
    if player_index is None:
        # Try to find by matching username in game players
        for idx, player in enumerate(game.players):
            if player.name == user_id:
                player_index = idx
                manager.user_to_player_index[user_id] = idx
                break
        if player_index is None:
            await manager.send_personal_message({
                "type": "error",
                "message": "Could not determine your player position"
            }, user_id)
            return
    
    contract_type = message.get("contract")
    trump_suit = message.get("trump_suit")
    called_ace = message.get("called_ace")
    
    # Convert to enums - handle string values
    trump_suit_enum = None
    if trump_suit:
        try:
            trump_suit_enum = Suit(trump_suit)
        except (ValueError, KeyError):
            print(f"Invalid trump suit: {trump_suit}")
    
    called_ace_enum = None
    if called_ace:
        try:
            called_ace_enum = Suit(called_ace)
        except (ValueError, KeyError):
            print(f"Invalid called ace: {called_ace}")
    
    # Make the bid
    try:
        bid_result = game.make_bid(player_index, contract_type, trump_suit_enum, called_ace_enum)
        if bid_result:
            await manager.broadcast_to_game({
                "type": "bid_made",
                "player_id": user_id,
                "player_index": player_index,
                "contract": contract_type,
                "trump_suit": trump_suit,
                "called_ace": called_ace
            }, game_id)
            
            await broadcast_game_state(game_id)
        else:
            # Provide more specific error message
            if player_index != game.current_bidder_index:
                error_msg = f"Not your turn. Current bidder: {game.current_bidder_index}, you are: {player_index}"
            elif game.highest_bid:
                error_msg = "Your bid is too low. You must bid higher than the current highest bid."
            else:
                error_msg = "Invalid bid (bidding phase may have ended or invalid state)"
            
            await manager.send_personal_message({
                "type": "error",
                "message": error_msg
            }, user_id)
    except Exception as e:
        print(f"Error making bid: {e}")
        import traceback
        traceback.print_exc()
        await manager.send_personal_message({
            "type": "error",
            "message": f"Error processing bid: {str(e)}"
        }, user_id)

async def handle_get_state(game_id: str, user_id: str):
    """Send current game state to requesting player"""
    print(f"handle_get_state called for user_id={user_id}, game_id={game_id}")
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
    # Use the actual player mapping, not enumerate
    for user_id in manager.game_players.get(game_id, []):
        # Get player index from mapping
        player_index = manager.user_to_player_index.get(user_id)
        if player_index is None:
            # Try to find by matching username
            for idx, player in enumerate(game.players):
                if player.name == user_id:
                    player_index = idx
                    manager.user_to_player_index[user_id] = idx
                    break
        if player_index is not None:
            await send_game_state_to_user(game_id, user_id, player_index=player_index)

async def send_game_state_to_user(game_id: str, user_id: str, player_index: int = None):
    """Send game state to a specific user"""
    if game_id not in manager.games:
        return
    
    game = manager.games[game_id]
    
    # Determine player index from mapping - try multiple ways to find it
    if player_index is None:
        player_index = manager.user_to_player_index.get(user_id)
        # If not found, try to find by matching username in game players
        if player_index is None:
            for idx, player in enumerate(game.players):
                if player.name == user_id:
                    player_index = idx
                    # Update mapping for future use
                    manager.user_to_player_index[user_id] = idx
                    print(f"Found player {user_id} at index {idx} by matching name")
                    break
        
        # Still not found? Default to 0 but log warning
        if player_index is None:
            print(f"ERROR: Could not find player index for user_id: {user_id}")
            print(f"  Available mappings: {manager.user_to_player_index}")
            print(f"  Game players: {[p.name for p in game.players]}")
            print(f"  Game ID: {game_id}")
            player_index = 0
    
    # Validate player_index
    if player_index >= len(game.players):
        print(f"Error: player_index {player_index} out of range for {len(game.players)} players")
        player_index = 0
    
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
    
    # Get actual player names from game players
    player_names = [p.name for p in game.players]
    
    print(f"Sending game state to {user_id}:")
    print(f"  Player index: {player_index}")
    print(f"  Player names: {player_names}")
    print(f"  Your hand size: {len(player_hand)}")
    print(f"  Other hands: {other_hands}")
    
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
        "players": player_names,
        "your_player_index": player_index,  # CRITICAL: Include this!
        "bidding_phase": game.bidding_phase and not game.bidding_complete,
        "current_bidder": game.current_bidder_index if game.bidding_phase else None,
        "highest_bid": game.highest_bid,
        "passes_in_a_row": game.passes_in_a_row
    }
    
    print(f"  State being sent - current_player: {state['current_player']}, your_player_index: {state['your_player_index']}")
    
    await manager.send_personal_message({
        "type": "game_state",
        "state": state
    }, user_id)

async def handle_round_complete(game_id: str):
    """Handle round completion - calculate scores and save to database"""
    if game_id not in manager.games:
        return
    
    game = manager.games[game_id]
    
    if not game.contract:
        print(f"Warning: Round complete but no contract set for game {game_id}")
        return
    
    try:
        # Calculate scores
        round_score = game.calculate_scores()
        from app.game_logic.scoring import calculate_game_points
        game_points = calculate_game_points(round_score, game.contract_type)
        
        # Get room to access user IDs
        room = manager.game_rooms.get(game_id)
        if not room:
            print(f"Warning: No room found for game {game_id}")
            return
        
        # Save game records and update stats for all players
        from app.database.database import SessionLocal
        from app.database.models import User, GameRecord, PlayerStats
        from datetime import datetime
        
        db = SessionLocal()
        try:
            # Get usernames from game players (these match the websocket user_ids)
            usernames = [p.name for p in game.players]
            
            # Map usernames to database user IDs
            user_id_map = {}  # username -> integer user_id
            for player_info in room.players:
                user_id_map[player_info["username"]] = player_info["user_id"]
            
            # Determine which players won (declarer team)
            declarer_won = round_score["won"]
            if game.contract_type == "Rufer" and game.partner_index is not None:
                # Partnership game
                winning_team = [game.declarer_index, game.partner_index]
            else:
                # Solo game
                winning_team = [game.declarer_index]
            
            # Save GameRecord and update PlayerStats for each player
            for player_index, username in enumerate(usernames):
                # Get integer user_id from map
                user_id = user_id_map.get(username)
                if not user_id:
                    print(f"Warning: Could not find user_id for username {username}")
                    continue
                # Get user from database
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    print(f"Warning: User {user_id} not found in database")
                    continue
                
                # Determine if this player won
                player_won = player_index in winning_team and declarer_won
                
                # Create GameRecord
                # Calculate points for this player
                # game_points is from declarer's perspective, so negate for opponents
                if player_index in winning_team:
                    # Player is on winning team - use game_points as-is
                    player_game_points = game_points
                else:
                    # Player is on losing team - negate the points
                    player_game_points = -game_points
                
                game_record = GameRecord(
                    game_id=game_id,
                    user_id=user_id,
                    contract_type=game.contract_type,
                    declarer_index=game.declarer_index,
                    partner_index=game.partner_index,
                    won=player_won,
                    schneider=round_score["schneider"],
                    schwarz=round_score["schwarz"],
                    declarer_points=round_score["declarer_points"],
                    team_points=round_score["team_points"],
                    game_points=player_game_points,
                    created_at=datetime.utcnow()
                )
                db.add(game_record)
                
                # Update or create PlayerStats
                stats = db.query(PlayerStats).filter(PlayerStats.user_id == user_id).first()
                if not stats:
                    stats = PlayerStats(user_id=user_id)
                    db.add(stats)
                
                stats.games_played += 1
                if player_won:
                    stats.games_won += 1
                # Add absolute value of points to total (only positive points count)
                stats.total_points += abs(game_points) if player_won else 0
                if round_score["schneider"] and player_won:
                    stats.schneider_count += 1
                if round_score["schwarz"] and player_won:
                    stats.schwarz_count += 1
                stats.last_played = datetime.utcnow()
                stats.updated_at = datetime.utcnow()
            
            db.commit()
            
            # Broadcast round complete message
            await manager.broadcast_to_game({
                "type": "round_complete",
                "scores": round_score,
                "game_points": game_points,
                "message": f"Round complete! {'Declarer team won!' if declarer_won else 'Opponents won!'}"
            }, game_id)
            
        except Exception as e:
            db.rollback()
            print(f"Error saving game results: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error handling round completion: {e}")
        import traceback
        traceback.print_exc()
