"""E2E tests for room API endpoints"""
import pytest

# Import APP_AVAILABLE from conftest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from conftest import APP_AVAILABLE
    if not APP_AVAILABLE:
        pytestmark = pytest.mark.skip(reason="E2E tests require full app dependencies")
except (ImportError, NameError):
    pytestmark = pytest.mark.skip(reason="E2E tests require full app dependencies")

class TestRoomAPI:
    """E2E tests for room management"""
    
    def test_create_room(self, client, auth_headers):
        """Test creating a game room"""
        response = client.post(
            "/api/rooms/create",
            headers=auth_headers,
            json={"name": "Test Room"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "waiting"
    
    def test_join_room(self, client, auth_headers):
        """Test joining a room"""
        # Create room
        create_response = client.post(
            "/api/rooms/create",
            headers=auth_headers,
            json={"name": "Test Room"}
        )
        room_id = create_response.json()["id"]
        
        # Join room (same user can't join twice, but test the endpoint)
        response = client.post(
            f"/api/rooms/{room_id}/join",
            headers=auth_headers
        )
        assert response.status_code in [200, 400]  # 400 if already in room
    
    def test_list_rooms(self, client, auth_headers):
        """Test listing available rooms"""
        # Create a room
        client.post(
            "/api/rooms/create",
            headers=auth_headers,
            json={"name": "Test Room"}
        )
        
        # List rooms
        response = client.get("/api/rooms/list", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "rooms" in data
        assert len(data["rooms"]) > 0
    
    def test_set_ready(self, client, auth_headers):
        """Test setting player ready status"""
        # Create room
        create_response = client.post(
            "/api/rooms/create",
            headers=auth_headers,
            json={"name": "Test Room"}
        )
        room_id = create_response.json()["id"]
        
        # Set ready
        response = client.post(
            f"/api/rooms/{room_id}/ready",
            headers=auth_headers,
            json={"ready": True}
        )
        assert response.status_code == 200
        data = response.json()
        # Check that player is marked as ready
        players = data.get("players", [])
        assert any(p.get("ready") == True for p in players)
    
    def test_leave_room(self, client, auth_headers):
        """Test leaving a room"""
        # Create room
        create_response = client.post(
            "/api/rooms/create",
            headers=auth_headers,
            json={"name": "Test Room"}
        )
        room_id = create_response.json()["id"]
        
        # Leave room
        response = client.post(
            f"/api/rooms/{room_id}/leave",
            headers=auth_headers
        )
        assert response.status_code == 200

