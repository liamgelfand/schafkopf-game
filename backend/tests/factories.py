"""Test data factories for creating test objects"""
from typing import Optional
from faker import Faker
from app.database.models import User
from app.auth.security import get_password_hash
from app.models.game import Game
from app.models.card import Suit, Rank, Card
from app.models.player import Player

fake = Faker()


class UserFactory:
    """Factory for creating test users"""
    
    @staticmethod
    def create(
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: str = "test123",
        is_active: bool = True,
        email_verified: bool = True
    ) -> User:
        """Create a test user"""
        return User(
            username=username or fake.user_name(),
            email=email or fake.email(),
            hashed_password=get_password_hash(password),
            is_active=is_active,
            email_verified=email_verified
        )


class GameFactory:
    """Factory for creating test games"""
    
    @staticmethod
    def create(
        game_id: Optional[str] = None,
        num_players: int = 4,
        deal_cards: bool = True
    ) -> Game:
        """Create a test game"""
        game = Game(game_id or fake.uuid4())
        for i in range(num_players):
            game.add_player(f"player{i+1}")
        if deal_cards:
            game.deal_cards()
        return game


class CardFactory:
    """Factory for creating test cards"""
    
    @staticmethod
    def create(suit: Optional[Suit] = None, rank: Optional[Rank] = None) -> Card:
        """Create a test card"""
        if suit is None:
            suit = fake.random_element(elements=list(Suit))
        if rank is None:
            rank = fake.random_element(elements=list(Rank))
        return Card(suit, rank)
    
    @staticmethod
    def create_hand(num_cards: int = 8) -> list[Card]:
        """Create a random hand of cards"""
        from app.models.deck import Deck
        deck = Deck()
        deck.shuffle()
        return deck.deal(1)[0][:num_cards]


class PlayerFactory:
    """Factory for creating test players"""
    
    @staticmethod
    def create(
        player_id: Optional[int] = None,
        name: Optional[str] = None,
        hand: Optional[list[Card]] = None,
        is_ai: bool = False
    ) -> Player:
        """Create a test player"""
        if player_id is None:
            player_id = fake.random_int(min=0, max=3)
        if name is None:
            name = f"player{player_id + 1}"
        
        player = Player(player_id, name, is_ai)
        if hand:
            player.hand = hand
        return player



