import pytest
from httpx import AsyncClient
from app.auth.security import hash_password, verify_password
from app.models.user import User

@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient) -> None:
    """Verifies that the health check endpoint returns 200 and stack status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "unhealthy")
    assert "services" in data
    assert "api" in data["services"]
    assert "database" in data["services"]
    assert "redis" in data["services"]

@pytest.mark.asyncio
async def test_user_registration_success(client: AsyncClient) -> None:
    """Tests registering a new user with valid details."""
    payload = {
        "email": "testregister@businessos.com",
        "full_name": "Test User Register",
        "password": "SuperSecurePassword123!",
        "role": "EMPLOYEE",
        "phone": "+15555551234",
        "company_name": "Test Org",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert "id" in data
    assert data["is_active"] is True
    assert data["is_verified"] is False

@pytest.mark.asyncio
async def test_user_registration_weak_password(client: AsyncClient) -> None:
    """Tests registering a new user with a weak password fails validation."""
    payload = {
        "email": "weakpass@businessos.com",
        "full_name": "Weak Pass User",
        "password": "123",  # fails minimum length & character rules
        "role": "EMPLOYEE",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "ValidationError"

@pytest.mark.asyncio
async def test_user_registration_duplicate_email(client: AsyncClient) -> None:
    """Tests registering a duplicate email returns 409 conflict error."""
    payload = {
        "email": "duplicate@businessos.com",
        "full_name": "Duplicate User",
        "password": "SuperSecurePassword123!",
        "role": "EMPLOYEE",
    }
    # Register first time
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Register second time
    res2 = await client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    data = res2.json()
    assert data["success"] is False
    assert data["error"]["code"] == "DuplicateEntityException"

@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient) -> None:
    """Tests successful credentials exchange for cookies and tokens."""
    # Register user first
    email = "testlogin@businessos.com"
    password = "SuperSecurePassword123!"
    reg_payload = {
        "email": email,
        "full_name": "Login User",
        "password": password,
        "role": "ADMIN",
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    # Attempt login
    login_payload = {
        "email": email,
        "password": password,
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == email

    # Verify cookie was set
    cookies = response.headers.get("set-cookie")
    assert "access_token=" in cookies

@pytest.mark.asyncio
async def test_user_login_invalid_credentials(client: AsyncClient) -> None:
    """Tests invalid login attempts fail with 401 status."""
    login_payload = {
        "email": "nonexistent@businessos.com",
        "password": "SuperSecurePassword123!",
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AuthenticationException"

@pytest.mark.asyncio
async def test_get_current_user_me_authenticated(client: AsyncClient) -> None:
    """Tests reading user context using Bearer tokens."""
    email = "getme@businessos.com"
    password = "SuperSecurePassword123!"
    reg_payload = {
        "email": email,
        "full_name": "Get Me User",
        "password": password,
        "role": "EMPLOYEE",
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    # Login to retrieve token
    login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_res.json()["access_token"]

    # Request /me
    headers = {"Authorization": f"Bearer {token}"}
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

@pytest.mark.asyncio
async def test_get_current_user_me_unauthenticated(client: AsyncClient) -> None:
    """Tests reading user context without headers fails with 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token_rotation_success(client: AsyncClient) -> None:
    """Tests rotating tokens using refresh tokens."""
    email = "refresh@businessos.com"
    password = "SuperSecurePassword123!"
    reg_payload = {
        "email": email,
        "full_name": "Refresh User",
        "password": password,
        "role": "EMPLOYEE",
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    # Login
    login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    refresh_token = login_res.json()["refresh_token"]

    # Refresh
    refresh_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    data = refresh_res.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Re-use of old refresh token must be blacklisted and fail
    reuse_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert reuse_res.status_code == 401
