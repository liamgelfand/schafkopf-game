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
    
    if not room.add_player(current_user.id, current_user.username):
        raise HTTPException(status_code=400, detail="Cannot join room")
    
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
    
    # Delete room if empty
    if len(room.players) == 0:
        del rooms[room_id]
        return {"message": "Room deleted"}
    
    return room.to_dict()

@router.post("/{room_id}/ready")
async def set_ready(
    room_id: str,
    request: ReadyRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Set player ready status"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms[room_id]
    room.set_player_ready(current_user.id, request.ready)
    
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
    
    game = room.start_game()
    manager.games[room_id] = game
    
    # Map user IDs to player indices (use username as key since token uses username)
    user_ids = [p["username"] for p in room.players]
    manager.set_player_mapping(room_id, user_ids)
    
    # Broadcast game started
    await manager.broadcast_to_game({
        "type": "game_started",
        "game_id": room_id,
        "players": [p["username"] for p in room.players]
    }, room_id)
    
    # Send initial game state to all players
    for idx, username in enumerate(user_ids):
        player_index = manager.user_to_player_index.get(username, idx)
        await manager.send_personal_message({
            "type": "game_state",
            "state": {
                "game_id": room_id,
                "current_trick": [],
                "current_player": 0,
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
                "players": [p.name for p in game.players]
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

