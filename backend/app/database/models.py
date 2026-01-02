from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    games = relationship("GameRecord", back_populates="player")
    stats = relationship("PlayerStats", back_populates="user", uselist=False)

class GameRecord(Base):
    """Database model for game records"""
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    contract_type = Column(String)
    declarer_index = Column(Integer)
    partner_index = Column(Integer, nullable=True)
    won = Column(Boolean)
    schneider = Column(Boolean)
    schwarz = Column(Boolean)
    declarer_points = Column(Integer)
    team_points = Column(Integer)
    game_points = Column(Integer)  # Calculated game points
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    player = relationship("User", back_populates="games")

class PlayerStats(Base):
    """Database model for player statistics"""
    __tablename__ = "player_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    games_played = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    schneider_count = Column(Integer, default=0)
    schwarz_count = Column(Integer, default=0)
    last_played = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="stats")
