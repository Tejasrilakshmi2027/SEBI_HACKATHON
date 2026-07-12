import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_signup(client: AsyncClient):
    """Test user signup endpoint."""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "testpassword123",
            "role": "investor"
        }
    )
    assert response.status_code in [200, 201]
    data = response.json()
    assert "id" in data
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    """Test signup with duplicate email."""
    # First signup
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "duplicate@example.com",
            "username": "user1",
            "full_name": "User One",
            "password": "password123",
            "role": "investor"
        }
    )
    
    # Duplicate signup
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "duplicate@example.com",
            "username": "user2",
            "full_name": "User Two",
            "password": "password123",
            "role": "investor"
        }
    )
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Test user login endpoint."""
    # First create a user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "full_name": "Login User",
            "password": "loginpassword123",
            "role": "investor"
        }
    )
    
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "loginpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code in [400, 401]


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """Test getting current user info."""
    # Create and login user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "current@example.com",
            "username": "currentuser",
            "full_name": "Current User",
            "password": "currentpassword123",
            "role": "investor"
        }
    )
    
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "current@example.com",
            "password": "currentpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "current@example.com"
    assert data["username"] == "currentuser"


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test getting current user without token."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_forgot_password(client: AsyncClient):
    """Test forgot password endpoint."""
    # Create user first
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "forgot@example.com",
            "username": "forgotuser",
            "full_name": "Forgot User",
            "password": "forgotpassword123",
            "role": "investor"
        }
    )
    
    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "forgot@example.com"}
    )
    assert response.status_code == 200
