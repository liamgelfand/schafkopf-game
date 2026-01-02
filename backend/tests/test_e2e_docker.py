"""
True End-to-End tests that require Docker containers to be running.

These tests make actual HTTP requests to the running API server.
Run with: docker-compose up -d && pytest tests/test_e2e_docker.py -v
"""
import pytest
import httpx
import os
from typing import Optional

# API base URL - defaults to Docker container, can be overridden
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

@pytest.fixture
async def api_client():
    """Create an HTTP client for API requests"""
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        yield client

@pytest.fixture
async def test_user(api_client):
    """Create a test user and return auth token"""
    import random
    import string
    
    # Generate unique username/email for each test run
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    username = f"testuser_{random_suffix}"
    email = f"test_{random_suffix}@example.com"
    password = "testpass123"
    
    # Register user
    register_response = await api_client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    
    if register_response.status_code not in [201, 400]:  # 201 Created, 400 if user exists
        pytest.fail(f"Failed to register user: {register_response.status_code} {register_response.text}")
    
    # Login to get token
    login_response = await api_client.post(
        "/api/auth/login",
        data={
            "username": username,
            "password": password
        }
    )
    
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    yield {
        "username": username,
        "email": email,
        "password": password,
        "token": token,
        "headers": headers
    }
    
    # Cleanup: Try to delete user (if endpoint exists)
    # For now, we'll just leave test users

@pytest.mark.asyncio
@pytest.mark.e2e_docker
class TestE2EDocker:
    """True E2E tests requiring Docker containers"""
    
    async def test_api_health_check(self, api_client):
        """Test that the API is running and accessible"""
        response = await api_client.get("/docs")  # FastAPI docs endpoint
        assert response.status_code == 200
    
    async def test_register_and_login(self, api_client):
        """Test user registration and login flow"""
        import random
        import string
        
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        username = f"e2e_user_{random_suffix}"
        email = f"e2e_{random_suffix}@example.com"
        password = "testpass123"
        
        # Register
        register_response = await api_client.post(
            "/api/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )
        assert register_response.status_code == 201  # 201 Created is correct for registration
        token_data = register_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Login
        login_response = await api_client.post(
            "/api/auth/login",
            data={
                "username": username,
                "password": password
            }
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Get current user
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        me_response = await api_client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["username"] == username
    
    async def test_create_room(self, api_client, test_user):
        """Test creating a game room"""
        response = await api_client.post(
            "/api/rooms/create",
            headers=test_user["headers"],
            json={"name": "E2E Test Room"}
        )
        assert response.status_code == 200
        room_data = response.json()
        assert "id" in room_data
        assert room_data["status"] == "waiting"
        # Note: room.to_dict() doesn't include "name" field, only id, creator_id, players, status, max_players, created_at
        assert len(room_data["players"]) == 1
        assert room_data["players"][0]["username"] == test_user["username"]
        return room_data["id"]
    
    async def test_join_room(self, api_client, test_user):
        """Test joining a game room"""
        # Create room with first user
        room_id = await self.test_create_room(api_client, test_user)
        
        # Create second user
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        username2 = f"e2e_user2_{random_suffix}"
        email2 = f"e2e2_{random_suffix}@example.com"
        
        register_response = await api_client.post(
            "/api/auth/register",
            json={
                "username": username2,
                "email": email2,
                "password": "testpass123"
            }
        )
        login_response = await api_client.post(
            "/api/auth/login",
            data={"username": username2, "password": "testpass123"}
        )
        token2 = login_response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Join room
        join_response = await api_client.post(
            f"/api/rooms/{room_id}/join",
            headers=headers2
        )
        assert join_response.status_code == 200
        room_data = join_response.json()
        assert len(room_data["players"]) == 2
        assert any(p["username"] == username2 for p in room_data["players"])
    
    async def test_full_game_flow_4_players(self, api_client):
        """Test complete game flow with 4 players"""
        import random
        import string
        
        # Create 4 users
        users = []
        for i in range(4):
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            username = f"player{i+1}_{random_suffix}"
            email = f"player{i+1}_{random_suffix}@example.com"
            
            # Register
            await api_client.post(
                "/api/auth/register",
                json={
                    "username": username,
                    "email": email,
                    "password": "testpass123"
                }
            )
            
            # Login
            login_response = await api_client.post(
                "/api/auth/login",
                data={"username": username, "password": "testpass123"}
            )
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            users.append({
                "username": username,
                "headers": headers
            })
        
        # Player 1 creates room
        create_response = await api_client.post(
            "/api/rooms/create",
            headers=users[0]["headers"],
            json={"name": "E2E Full Game Test"}
        )
        assert create_response.status_code == 200
        room_id = create_response.json()["id"]
        
        # Players 2, 3, 4 join
        for i in range(1, 4):
            join_response = await api_client.post(
                f"/api/rooms/{room_id}/join",
                headers=users[i]["headers"]
            )
            assert join_response.status_code == 200
        
        # All players set ready
        for i in range(4):
            ready_response = await api_client.post(
                f"/api/rooms/{room_id}/ready",
                headers=users[i]["headers"],
                json={"ready": True}
            )
            assert ready_response.status_code == 200
            room_data = ready_response.json()
            assert room_data["players"][i]["ready"] == True
        
        # After last player readies, game should start
        final_room = ready_response.json()
        assert final_room["status"] == "in_progress"
        
        # Verify game was created
        # (In a real E2E test, you'd also test WebSocket connection and game flow)
        return room_id
    
    async def test_list_rooms(self, api_client, test_user):
        """Test listing available rooms"""
        # Create a room first
        await self.test_create_room(api_client, test_user)
        
        # List rooms
        response = await api_client.get(
            "/api/rooms/list",
            headers=test_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert "rooms" in data
        rooms = data["rooms"]
        assert isinstance(rooms, list)
        assert len(rooms) > 0

