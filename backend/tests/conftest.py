"""Pytest configuration and shared fixtures"""
import pytest
import os

# Only import app-related modules when needed (for E2E tests)
# This allows unit tests to run without full app dependencies
try:
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.main import app
    from app.database.database import Base, get_db
    from app.database.models import User
    from app.auth.security import get_password_hash
    APP_AVAILABLE = True
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except ImportError as e:
    APP_AVAILABLE = False
    # Create dummy objects for unit tests that don't need the app
    TestClient = None
    app = None
    engine = None
    TestingSessionLocal = None

# Export APP_AVAILABLE for use in test files
__all__ = ['APP_AVAILABLE']

# Only define these fixtures if app is available
if APP_AVAILABLE:

    @pytest.fixture(scope="function")
    def db():
        """Create a fresh database for each test"""
        Base.metadata.create_all(bind=engine)
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
        Base.metadata.drop_all(bind=engine)

    @pytest.fixture(scope="function")
    def client(db):
        """Create a test client with database override"""
        def override_get_db():
            try:
                yield db
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        test_client = TestClient(app)
        yield test_client
        app.dependency_overrides.clear()

    @pytest.fixture
    def test_user(db):
        """Create a test user"""
        try:
            password_hash = get_password_hash("test123")  # Shorter password
        except ValueError:
            # Fallback if bcrypt has issues - use a simple hash for testing
            import hashlib
            password_hash = hashlib.sha256("test123".encode()).hexdigest()
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=password_hash
        )
        user.email_verified = True  # Set after creation
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @pytest.fixture
    def auth_headers(client, test_user):
        """Get authentication headers for test user"""
        response = client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "test123"}  # Match test_user password
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def game():
    """Create a test game instance"""
    from app.models.game import Game
    game = Game("test-game")
    for i in range(4):
        game.add_player(f"player{i+1}")
    game.deal_cards()
    return game

