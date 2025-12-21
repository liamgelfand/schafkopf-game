from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, GameRecord, PlayerStats
from app.auth.security import get_current_active_user
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class CreateGameRequest(BaseModel):
    pass

class MakeMoveRequest(BaseModel):
    card: dict

class PassRequest(BaseModel):
    pass_action: bool = True

class GameStateResponse(BaseModel):
    gameId: str
    state: dict

@router.post("/game/create")
async def create_game(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new game"""
    import uuid
    game_id = str(uuid.uuid4())
    
    # Create game record
    game_record = GameRecord(
        game_id=game_id,
        user_id=current_user.id,
        contract_type="Rufer",  # Default
        created_at=datetime.utcnow()
    )
    db.add(game_record)
    db.commit()
    
    return {"gameId": game_id, "message": "Game created"}

@router.post("/game/{game_id}/move")
async def make_move(
    game_id: str,
    request: MakeMoveRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Make a move in the game"""
    # Verify game belongs to user
    game_record = db.query(GameRecord).filter(
        GameRecord.game_id == game_id,
        GameRecord.user_id == current_user.id
    ).first()
    
    if not game_record:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return {"message": "Move handled", "gameId": game_id}

@router.get("/game/{game_id}/state")
async def get_game_state(
    game_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current game state"""
    game_record = db.query(GameRecord).filter(
        GameRecord.game_id == game_id,
        GameRecord.user_id == current_user.id
    ).first()
    
    if not game_record:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return {"gameId": game_id, "state": "placeholder"}

@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's statistics"""
    stats = db.query(PlayerStats).filter(
        PlayerStats.user_id == current_user.id
    ).first()
    
    if not stats:
        # Create stats if they don't exist
        stats = PlayerStats(user_id=current_user.id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    
    return {
        "gamesPlayed": stats.games_played,
        "gamesWon": stats.games_won,
        "winRate": (stats.games_won / stats.games_played * 100) if stats.games_played > 0 else 0,
        "totalPoints": stats.total_points,
        "schneiderCount": stats.schneider_count,
        "schwarzCount": stats.schwarz_count,
    }

@router.post("/game/{game_id}/pass")
async def pass_turn(
    game_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Pass turn in the game"""
    game_record = db.query(GameRecord).filter(
        GameRecord.game_id == game_id,
        GameRecord.user_id == current_user.id
    ).first()
    
    if not game_record:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return {"message": "Turn passed", "gameId": game_id}

@router.get("/history")
async def get_game_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 20
):
    """Get user's game history"""
    games = db.query(GameRecord).filter(
        GameRecord.user_id == current_user.id
    ).order_by(GameRecord.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": game.game_id,
            "contractType": game.contract_type,
            "won": game.won if game.won is not None else False,
            "points": game.game_points or 0,
            "schneider": game.schneider if game.schneider is not None else False,
            "schwarz": game.schwarz if game.schwarz is not None else False,
            "date": game.created_at.isoformat() if game.created_at else "",
        }
        for game in games
    ]
