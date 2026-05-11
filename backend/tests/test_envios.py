"""Integration tests for envios (shipping config) endpoints."""

import pytest

from app.config import settings
from app.usuarios.service import seed_admin


async def _login(async_client):
    resp = await async_client.post("/auth/login", json={
        "email": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASSWORD,
    })
    return resp.json()["access_token"]


async def _auth_headers(async_client):
    token = await _login(async_client)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_config_defaults(async_client, db_session):
    """GIVEN no config in DB → returns defaults (CABA:3500, GBA_NORTE:3500)."""
    await seed_admin(db_session)

    response = await async_client.get("/envios/config")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    zonas = {item["zona"]: item["costo"] for item in data}
    assert zonas["CABA"] == "3500.00"
    assert zonas["GBA_NORTE"] == "3500.00"


@pytest.mark.asyncio
async def test_update_config(async_client, db_session):
    """GIVEN admin token + valid zones → config updated."""
    await seed_admin(db_session)
    headers = await _auth_headers(async_client)

    response = await async_client.put(
        "/envios/config",
        json={
            "zonas": [
                {"zona": "CABA", "costo": "4000.00"},
                {"zona": "GBA_SUR", "costo": "5000.00"},
            ],
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    zonas = {item["zona"]: item["costo"] for item in data}
    assert zonas["CABA"] == "4000.00"
    assert zonas["GBA_SUR"] == "5000.00"

    # Verify GET returns updated config
    get_resp = await async_client.get("/envios/config")
    get_data = get_resp.json()
    assert len(get_data) == 2


@pytest.mark.asyncio
async def test_update_config_requires_auth(async_client):
    """GIVEN no auth → 401."""
    response = await async_client.put(
        "/envios/config",
        json={"zonas": [{"zona": "CABA", "costo": "4000.00"}]},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_config_after_update(async_client, db_session):
    """GIVEN config was updated → GET returns updated values."""
    await seed_admin(db_session)
    headers = await _auth_headers(async_client)

    await async_client.put(
        "/envios/config",
        json={
            "zonas": [
                {"zona": "CABA", "costo": "4500.00"},
            ],
        },
        headers=headers,
    )

    response = await async_client.get("/envios/config")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["zona"] == "CABA"
    assert data[0]["costo"] == "4500.00"
