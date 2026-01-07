from typing import List, Optional, Dict
from datetime import datetime
import secrets
from app.models.game import Game
from app.models.player import Player
from app.models.card import Suit

class GameRoom:
    """Represents a game room waiting for players"""
    
    def __init__(self, room_id: str, creator_id: int, creator_username: str, is_private: bool = False):
        self.room_id = room_id
        self.creator_id = creator_id
        self.players: List[Dict] = []  # List of {user_id, username, ready}
        self.status: str = "waiting"  # waiting, starting, in_progress
        self.created_at = datetime.utcnow()
        self.game: Optional[Game] = None
        self.max_players = 4
        self.is_private = is_private
        self.join_code = secrets.token_urlsafe(6).upper() if is_private else None  # 6-character code for private rooms
    
    def add_player(self, user_id: int, username: str) -> bool:
        """Add a player to the room"""
        if len(self.players) >= self.max_players:
            return False
        
        # Check if player already in room
        if any(p["user_id"] == user_id for p in self.players):
            return False
        
        self.players.append({
            "user_id": user_id,
            "username": username,
            "ready": False
        })
        return True
    
    def remove_player(self, user_id: int):
        """Remove a player from the room"""
        self.players = [p for p in self.players if p["user_id"] != user_id]
    
    def set_player_ready(self, user_id: int, ready: bool):
        """Set player ready status"""
        for player in self.players:
            if player["user_id"] == user_id:
                player["ready"] = ready
                break
    
    def all_ready(self) -> bool:
        """Check if all players are ready"""
        return len(self.players) == self.max_players and all(p["ready"] for p in self.players)
    
    def start_game(self):
        """Initialize the game with all players"""
        if not self.all_ready():
            raise ValueError("Not all players are ready")
        
        self.game = Game(self.room_id)
        
        # Add all players (no AI)
        for player in self.players:
            self.game.add_player(player["username"], is_ai=False)
        
        # Deal cards
        self.game.deal_cards()
        self.status = "in_progress"
        
        return self.game
    
    def to_dict(self):
        """Convert room to dictionary for API responses"""
        return {
            "id": self.room_id,
            "creator_id": self.creator_id,
            "players": self.players,
            "status": self.status,
            "max_players": self.max_players,
            "created_at": self.created_at.isoformat(),
            "is_private": self.is_private,
            "join_code": self.join_code
        }

