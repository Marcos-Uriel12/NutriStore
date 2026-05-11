"""Integration tests for auth endpoints."""

import pytest

from app.config import settings
from app.usuarios.service import seed_admin


@pytest.mark.asyncio
async def test_login_success(async_client, db_session):
    """GIVEN admin exists + valid credentials → 200 with token."""
    await seed_admin(db_session)

    response = await async_client.post("/auth/login", json={
        "email": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASSWORD,
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(async_client, db_session):
    """GIVEN admin exists + invalid password → 401."""
    await seed_admin(db_session)

    response = await async_client.post("/auth/login", json={
        "email": settings.ADMIN_EMAIL,
        "password": "wrong-password",
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_invalid_email(async_client, db_session):
    """GIVEN no admin with that email → 401."""
    await seed_admin(db_session)

    response = await async_client.post("/auth/login", json={
        "email": "nonexistent@nutristore.com",
        "password": "anything",
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_valid_token(async_client, db_session):
    """GIVEN valid JWT → 200 with admin info."""
    await seed_admin(db_session)

    # Login to get token
    login_response = await async_client.post("/auth/login", json={
        "email": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASSWORD,
    })
    token = login_response.json()["access_token"]

    response = await async_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == settings.ADMIN_EMAIL
    assert "id" in data


@pytest.mark.asyncio
async def test_me_without_token(async_client):
    """GIVEN no token → 401."""
    response = await async_client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_invalid_token(async_client):
    """GIVEN malformed token → 401."""
    response = await async_client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token-value"},
    )
    assert response.status_code == 401
