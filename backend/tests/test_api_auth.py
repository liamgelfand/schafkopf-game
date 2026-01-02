"""E2E tests for authentication API"""
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

class TestAuthAPI:
    """E2E tests for authentication endpoints"""
    
    def test_register_user(self, client):
        """Test user registration"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepass123"
            }
        )
        assert response.status_code == 201  # 201 Created is correct for registration
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_user(self, client, test_user):
        """Test user login"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "testuser",
                "password": "test123"  # Match password from test_user fixture
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info"""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "email" in data
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

