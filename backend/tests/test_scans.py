import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_scan_unauthorized(client: AsyncClient):
    """Test file upload without authentication."""
    response = await client.post(
        "/api/v1/scans/upload",
        files={"file": ("test.txt", b"test content", "text/plain")},
        data={"scan_type": "text"}
    )
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_upload_scan_authorized(client: AsyncClient):
    """Test file upload with authentication."""
    # Create and login user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "scan@example.com",
            "username": "scanuser",
            "full_name": "Scan User",
            "password": "scanpassword123",
            "role": "investor"
        }
    )
    
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "scan@example.com",
            "password": "scanpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Upload file
    response = await client.post(
        "/api/v1/scans/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.txt", b"test content", "text/plain")},
        data={"scan_type": "text"}
    )
    assert response.status_code in [200, 202]
    data = response.json()
    assert "scan_id" in data
    assert data["status"] in ["processing", "queued"]


@pytest.mark.asyncio
async def test_scan_url(client: AsyncClient):
    """Test URL scanning."""
    # Create and login user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "urlscan@example.com",
            "username": "urlscanuser",
            "full_name": "URL Scan User",
            "password": "urlscanpassword123",
            "role": "investor"
        }
    )
    
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "urlscan@example.com",
            "password": "urlscanpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Scan URL
    response = await client.post(
        "/api/v1/scans/scan-url",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "url": "https://example.com",
            "scan_type": "url"
        }
    )
    assert response.status_code in [200, 202]
    data = response.json()
    assert "scan_id" in data


@pytest.mark.asyncio
async def test_get_scan_result(client: AsyncClient):
    """Test getting scan results."""
    # Create and login user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "result@example.com",
            "username": "resultuser",
            "full_name": "Result User",
            "password": "resultpassword123",
            "role": "investor"
        }
    )
    
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "result@example.com",
            "password": "resultpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get scan result (may not exist yet)
    response = await client.get(
        "/api/v1/scans/test_scan_id",
        headers={"Authorization": f"Bearer {token}"}
    )
    # May return 404 if scan doesn't exist
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_get_scan_history(client: AsyncClient):
    """Test getting scan history."""
    # Create and login user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "history@example.com",
            "username": "historyuser",
            "full_name": "History User",
            "password": "historypassword123",
            "role": "investor"
        }
    )
    
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "history@example.com",
            "password": "historypassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get scan history
    response = await client.get(
        "/api/v1/scans/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "scans" in data
    assert "total" in data
