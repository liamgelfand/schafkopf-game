from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.database.database import get_db
from app.database.models import User
from app.auth.security import get_current_active_user
from app.models.room import GameRoom
from app.api.websocket import manager
from pydantic import BaseModel
from app.models.game import Game

router = APIRouter(prefix="/rooms", tags=["rooms"])

class CreateRoomRequest(BaseModel):
    name: str = "Game Room"

class JoinRoomRequest(BaseModel):
    room_id: str

class ReadyRequest(BaseModel):
    ready: bool

# In-memory room storage (in production, use Redis or database)
rooms: dict[str, GameRoom] = {}

@router.post("/create")
async def create_room(
    request: CreateRoomRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new game room"""
    room_id = str(uuid.uuid4())
    room = GameRoom(room_id, current_user.id, current_user.username)
    room.add_player(current_user.id, current_user.username)
    rooms[room_id] = room
    
    return room.to_dict()

@router.get("/list")
async def list_rooms(
    current_user: User = Depends(get_current_active_user)
):
    """List all available rooms"""
    available_rooms = [
        room.to_dict() 
        for room in rooms.values() 
        if room.status == "waiting" and len(room.players) < room.max_players
    ]
    return {"rooms": available_rooms}

@router.post("/{room_id}/join")
async def join_room(
    room_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Join a game room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms[room_id]
    
    if room.status != "waiting":
        raise HTTPException(status_code=400, detail="Room is not accepting players")
    
    # Check if player is already in room
    if any(p["user_id"] == current_user.id for p in room.players):
        # Player already in room, just return current room state
        return room.to_dict()
    
    if not room.add_player(current_user.id, current_user.username):
        raise HTTPException(status_code=400, detail="Cannot join room (room is full)")
    
    return room.to_dict()

@router.post("/{room_id}/leave")
async def leave_room(
    room_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Leave a game room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms[room_id]
    room.remove_player(current_user.id)
    
    # Clean up WebSocket connections
    from app.api.websocket import manager
    username = current_user.username
    if username in manager.active_connections:
        manager.disconnect(username)
    
    # If game is in progress, notify other players
    if room.status == "in_progress" and room_id in manager.games:
        await manager.broadcast_to_game({
            "type": "player_left",
            "user_id": username,
            "message": f"{username} left the game"
        }, room_id)
    
    # Delete room if empty
    if len(room.players) == 0:
        # Clean up game if it exists
        if room_id in manager.games:
            del manager.games[room_id]
        if room_id in manager.game_rooms:
            del manager.game_rooms[room_id]
        del rooms[room_id]
        return {"message": "Room deleted"}
    
    return room.to_dict()

@router.post("/{room_id}/ready")
async def set_ready(
    room_id: str,
    request: ReadyRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Set player ready status and auto-start if all ready"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms[room_id]
    room.set_player_ready(current_user.id, request.ready)
    
    # Auto-start game if all players are ready
    if room.all_ready() and room.status == "waiting":
        import random
        from app.api.websocket import manager
        
        # Start the game
        game = room.start_game()
        manager.games[room_id] = game
        manager.game_rooms[room_id] = room
        
        # Randomly select starting player for bidding
        game.current_bidder_index = random.randint(0, 3)
        game.current_player_index = game.current_bidder_index
        game.initial_bidder_index = game.current_bidder_index  # Track for reshuffle logic
        
        # Map user IDs to player indices - IMPORTANT: Use the order players were added to game
        user_ids = [p["username"] for p in room.players]
        print(f"Setting player mapping for game {room_id}:")
        print(f"  Room players order: {user_ids}")
        print(f"  Game players order: {[p.name for p in game.players]}")
        manager.set_player_mapping(room_id, user_ids)
        print(f"  Player mapping set: {manager.user_to_player_index}")
        
        # Broadcast game started
        await manager.broadcast_to_game({
            "type": "game_started",
            "game_id": room_id,
            "players": [p.name for p in game.players],  # Use game players, not room players
            "starting_bidder": game.current_bidder_index
        }, room_id)
        
        # Send initial game state to all players using the proper function
        # Import here to avoid circular import issues
        from app.api.websocket import send_game_state_to_user
        for idx, username in enumerate(user_ids):
            player_index = idx  # Use index directly since we know the order
            print(f"Sending initial game state to {username} at index {player_index}")
            # Use the send_game_state_to_user function which handles everything correctly
            await send_game_state_to_user(room_id, username, player_index=player_index)
    
    return room.to_dict()

@router.post("/{room_id}/start")
async def start_game(
    room_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Start the game (only if all players ready)"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms[room_id]
    
    if room.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only room creator can start")
    
    if not room.all_ready():
        raise HTTPException(status_code=400, detail="Not all players are ready")
    
    import random
    game = room.start_game()
    manager.games[room_id] = game
    manager.game_rooms[room_id] = room
    
    # Randomly select starting player for bidding (dealer)
    starting_bidder = random.randint(0, 3)
    game.current_bidder_index = starting_bidder
    game.current_player_index = starting_bidder
    
    # Map user IDs to player indices - IMPORTANT: Use the order players were added to game
    user_ids = [p["username"] for p in room.players]
    print(f"Setting player mapping for game {room_id}:")
    print(f"  Room players order: {user_ids}")
    print(f"  Game players order: {[p.name for p in game.players]}")
    manager.set_player_mapping(room_id, user_ids)
    print(f"  Player mapping set: {manager.user_to_player_index}")
    
    # Broadcast game started
    await manager.broadcast_to_game({
        "type": "game_started",
        "game_id": room_id,
        "players": [p.name for p in game.players],  # Use game players, not room players
        "starting_bidder": starting_bidder
    }, room_id)
    
    # Send initial game state to all players
    for idx, username in enumerate(user_ids):
        player_index = idx  # Use index directly since we know the order
        print(f"Sending game state to {username} at index {player_index}")
        await manager.send_personal_message({
            "type": "game_state",
            "state": {
                "game_id": room_id,
                "current_trick": [],
                "current_player": game.current_player_index,
                "your_hand": [
                    {"suit": c.suit.value, "rank": c.rank.value, "value": c.value}
                    for c in game.players[player_index].hand
                ],
                "other_hands": [
                    len(p.hand) if i != player_index else None
                    for i, p in enumerate(game.players)
                ],
                "contract": None,
                "trick_number": 0,
                "round_complete": False,
                "players": [p.name for p in game.players],
                "your_player_index": player_index,
                "bidding_phase": game.bidding_phase and not game.bidding_complete,
                "current_bidder": game.current_bidder_index if game.bidding_phase else None,
                "highest_bid": game.highest_bid,
                "passes_in_a_row": game.passes_in_a_row
            }
        }, username)
    
    return {"message": "Game started", "game_id": room_id}

@router.get("/{room_id}")
async def get_room(
    room_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get room information"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return rooms[room_id].to_dict()

