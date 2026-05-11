"""Integration tests for categorias and productos endpoints."""

import pytest

from app.config import settings
from app.usuarios.service import seed_admin


# ── Helpers ─────────────────────────────────────────────────────────────


async def _login(async_client):
    """Return a valid JWT token."""
    resp = await async_client.post("/auth/login", json={
        "email": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASSWORD,
    })
    return resp.json()["access_token"]


async def _auth_headers(async_client):
    token = await _login(async_client)
    return {"Authorization": f"Bearer {token}"}


# ── Categorias ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_categoria(async_client, db_session):
    """GIVEN admin JWT + valid payload → 201 with category."""
    await seed_admin(db_session)
    headers = await _auth_headers(async_client)

    response = await async_client.post(
        "/categorias",
        json={"nombre": "Lácteos", "descripcion": "Productos lácteos"},
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Lácteos"
    assert data["descripcion"] == "Productos lácteos"


@pytest.mark.asyncio
async def test_create_duplicate_categoria(async_client, db_session):
    """GIVEN duplicate name → 409 Conflict."""
    await seed_admin(db_session)
    headers = await _auth_headers(async_client)

    await async_client.post(
        "/categorias",
        json={"nombre": "Lácteos"},
        headers=headers,
    )
    response = await async_client.post(
        "/categorias",
        json={"nombre": "Lácteos"},
        headers=headers,
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_categorias_empty(async_client, db_session):
    """GIVEN no categories → empty array."""
    await seed_admin(db_session)

    response = await async_client.get("/categorias")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_categorias(async_client, db_session):
    """GIVEN categories exist → array."""
    await seed_admin(db_session)
    headers = await _auth_headers(async_client)

    await async_client.post("/categorias", json={"nombre": "Lácteos"}, headers=headers)
    await async_client.post("/categorias", json={"nombre": "Frutas"}, headers=headers)

    response = await async_client.get("/categorias")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {c["nombre"] for c in data} == {"Frutas", "Lácteos"}


# ── Productos ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_producto(async_client, db_session):
    """GIVEN admin JWT + valid payload → producto created."""
    await seed_admin(db_session)
    headers = await _auth_headers(async_client)

    # Create category first
    resp = await async_client.post(
        "/categorias", json={"nombre": "Lácteos"}, headers=headers,
    )
    cat_id = resp.json()["id"]

    response = await async_client.post(
        "/productos",
        json={
            "nombre": "Queso Fresco",
            "descripcion": "Queso fresco artesanal",
            "precio_por_kg": 1200.50,
            "tipo_unidad": "KG",
            "stock_kg": 5.0,
            "categoria_id": cat_id,
            "imagenes": [
                {"url": "https://example.com/queso1.jpg"},
                {"url": "https://example.com/queso2.jpg"},
            ],
        },
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Queso Fresco"
    assert data["precio_por_kg"] == 1200.5
    assert data["tipo_unidad"] == "KG"
    assert data["stock_kg"] == 5.0
    assert data["activo"] is True
    assert len(data["imagenes"]) == 2


@pytest.mark.asyncio
async def test_create_producto_max_images(async_client, db_session):
    """GIVEN 3+ images → 422 Validation Error."""
    await seed_admin(db_session)
    headers = await _auth_headers(async_client)

    resp = await async_client.post(
        "/categorias", json={"nombre": "Lácteos"}, headers=headers,
    )
    cat_id = resp.json()["id"]

    response = await async_client.post(
        "/productos",
        json={
            "nombre": "Queso",
            "precio_por_kg": 1000,
            "tipo_unidad": "KG",
            "categoria_id": cat_id,
            "imagenes": [
                {"url": "https://example.com/1.jpg"},
                {"url": "https://example.com/2.jpg"},
                {"url": "https://example.com/3.jpg"},
            ],
        },
        headers=headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_productos(async_client, db_session):
    """GIVEN products exist → returns list."""
    await seed_admin(db_session)
    headers = await _auth_headers(async_client)

    resp = await async_client.post(
        "/categorias", json={"nombre": "Lácteos"}, headers=headers,
    )
    cat_id = resp.json()["id"]

    await async_client.post(
        "/productos",
        json={
            "nombre": "Queso", "precio_por_kg": 1000,
            "tipo_unidad": "KG", "categoria_id": cat_id,
        },
        headers=headers,
    )
    await async_client.post(
        "/productos",
        json={
            "nombre": "Yogur", "precio_por_kg": 600,
            "tipo_unidad": "KG", "categoria_id": cat_id,
        },
        headers=headers,
    )

    response = await async_client.get("/productos")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {p["nombre"] for p in data} == {"Queso", "Yogur"}


@pytest.mark.asyncio
async def test_get_producto_by_id(async_client, db_session):
    """GIVEN product exists → returns detail."""
    await seed_admin(db_session)
    headers = await _auth_headers(async_client)

    resp = await async_client.post(
        "/categorias", json={"nombre": "Lácteos"}, headers=headers,
    )
    cat_id = resp.json()["id"]

    resp = await async_client.post(
        "/productos",
        json={
            "nombre": "Queso", "precio_por_kg": 1000,
            "tipo_unidad": "KG", "categoria_id": cat_id,
        },
        headers=headers,
    )
    prod_id = resp.json()["id"]

    response = await async_client.get(f"/productos/{prod_id}")

    assert response.status_code == 200
    assert response.json()["nombre"] == "Queso"


@pytest.mark.asyncio
async def test_get_producto_not_found(async_client):
    """GIVEN product does not exist → 404."""
    response = await async_client.get("/productos/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_producto(async_client, db_session):
    """GIVEN admin JWT + valid update → producto updated."""
    await seed_admin(db_session)
    headers = await _auth_headers(async_client)

    resp = await async_client.post(
        "/categorias", json={"nombre": "Lácteos"}, headers=headers,
    )
    cat_id = resp.json()["id"]

    resp = await async_client.post(
        "/productos",
        json={
            "nombre": "Queso", "precio_por_kg": 1000,
            "tipo_unidad": "KG", "categoria_id": cat_id,
        },
        headers=headers,
    )
    prod_id = resp.json()["id"]

    response = await async_client.put(
        f"/productos/{prod_id}",
        json={"nombre": "Queso Actualizado", "precio_por_kg": 1500},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Queso Actualizado"
    assert data["precio_por_kg"] == 1500


@pytest.mark.asyncio
async def test_delete_producto_soft(async_client, db_session):
    """GIVEN admin JWT → soft delete (activo=false)."""
    await seed_admin(db_session)
    headers = await _auth_headers(async_client)

    resp = await async_client.post(
        "/categorias", json={"nombre": "Lácteos"}, headers=headers,
    )
    cat_id = resp.json()["id"]

    resp = await async_client.post(
        "/productos",
        json={
            "nombre": "Queso", "precio_por_kg": 1000,
            "tipo_unidad": "KG", "categoria_id": cat_id,
        },
        headers=headers,
    )
    prod_id = resp.json()["id"]

    response = await async_client.delete(f"/productos/{prod_id}", headers=headers)
    assert response.status_code == 204

    # Verify product is no longer listed in active products
    list_resp = await async_client.get("/productos")
    assert len(list_resp.json()) == 0

    # But still reachable directly
    detail_resp = await async_client.get(f"/productos/{prod_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["activo"] is False


# ── Auth Guards ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_categoria_requires_auth(async_client):
    """GIVEN no auth → 401."""
    response = await async_client.post(
        "/categorias",
        json={"nombre": "Test"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_producto_requires_auth(async_client):
    """GIVEN no auth → 401."""
    response = await async_client.post(
        "/productos",
        json={
            "nombre": "Test", "precio_por_kg": 100,
            "tipo_unidad": "KG", "categoria_id": 1,
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_producto_requires_auth(async_client):
    """GIVEN no auth → 401."""
    response = await async_client.put(
        "/productos/1",
        json={"nombre": "Test"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_producto_requires_auth(async_client):
    """GIVEN no auth → 401."""
    response = await async_client.delete("/productos/1")
    assert response.status_code == 401
