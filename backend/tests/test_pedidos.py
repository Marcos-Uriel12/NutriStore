"""Integration tests for pedidos (orders) endpoints."""

import pytest

from app.config import settings
from app.usuarios.service import seed_admin


SESSION_ID = "order-session-xyz"


async def _login(async_client_with_redis):
    """Return a valid JWT token."""
    resp = await async_client_with_redis.post("/auth/login", json={
        "email": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASSWORD,
    })
    return resp.json()["access_token"]


async def _auth_headers(async_client_with_redis):
    token = await _login(async_client_with_redis)
    return {"Authorization": f"Bearer {token}"}


async def _create_category(async_client_with_redis, nombre="Lácteos"):
    headers = await _auth_headers(async_client_with_redis)
    resp = await async_client_with_redis.post(
        "/categorias",
        json={"nombre": nombre},
        headers=headers,
    )
    return resp.json()["id"]


async def _create_product(async_client_with_redis, cat_id, nombre="Queso Fresco"):
    headers = await _auth_headers(async_client_with_redis)
    resp = await async_client_with_redis.post(
        "/productos",
        json={
            "nombre": nombre,
            "precio_por_kg": 1200.50,
            "tipo_unidad": "KG",
            "stock_kg": 10.0,
            "categoria_id": cat_id,
        },
        headers=headers,
    )
    return resp.json()["id"]


async def _add_to_cart(async_client_with_redis, producto_id, cantidad=2.0, unidad="KG"):
    cart_headers = {"X-Session-ID": SESSION_ID}
    await async_client_with_redis.post(
        "/carrito",
        json={"producto_id": producto_id, "cantidad": cantidad, "unidad_medida": unidad},
        headers=cart_headers,
    )


# ── Create Pedido ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_pedido_empty_cart(async_client_with_redis):
    """GIVEN empty cart → 400 Bad Request."""
    response = await async_client_with_redis.post(
        "/pedidos",
        json={
            "cliente_nombre": "Juan",
            "cliente_direccion": "Calle 123",
            "cliente_telefono": "1112345678",
            "tipo_entrega": "RETIRO",
            "metodo_pago": "EFECTIVO",
        },
        headers={"X-Session-ID": SESSION_ID},
    )
    assert response.status_code == 400
    assert "Empty cart" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_pedido_retiro(async_client_with_redis, db_session):
    """GIVEN cart with items + RETIRO → order created, cart cleared."""
    await seed_admin(db_session)
    cat_id = await _create_category(async_client_with_redis)
    prod_id = await _create_product(async_client_with_redis, cat_id)
    await _add_to_cart(async_client_with_redis, prod_id, cantidad=2.0)

    response = await async_client_with_redis.post(
        "/pedidos",
        json={
            "cliente_nombre": "Juan Pérez",
            "cliente_direccion": "Calle Falsa 123",
            "cliente_telefono": "1112345678",
            "tipo_entrega": "RETIRO",
            "metodo_pago": "EFECTIVO",
        },
        headers={"X-Session-ID": SESSION_ID},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["cliente_nombre"] == "Juan Pérez"
    assert data["tipo_entrega"] == "RETIRO"
    assert data["costo_envio"] == "0.00"
    assert data["estado"] == "PENDIENTE"
    assert len(data["items"]) == 1
    assert data["items"][0]["producto_id"] == prod_id
    assert data["items"][0]["cantidad"] == 2.0
    assert data["pago"] is not None
    assert data["pago"]["metodo"] == "EFECTIVO"

    # Cart should be cleared
    cart_resp = await async_client_with_redis.get(
        "/carrito",
        headers={"X-Session-ID": SESSION_ID},
    )
    assert cart_resp.json() == []


@pytest.mark.asyncio
async def test_create_pedido_envio(async_client_with_redis, db_session):
    """GIVEN ENVIO with zona → includes shipping cost."""
    await seed_admin(db_session)
    cat_id = await _create_category(async_client_with_redis)
    prod_id = await _create_product(async_client_with_redis, cat_id)
    await _add_to_cart(async_client_with_redis, prod_id, cantidad=1.0)

    response = await async_client_with_redis.post(
        "/pedidos",
        json={
            "cliente_nombre": "María",
            "cliente_direccion": "Av. Siempre Viva 742",
            "cliente_telefono": "1198765432",
            "tipo_entrega": "ENVIO",
            "zona_envio": "CABA",
            "metodo_pago": "TRANSFERENCIA",
        },
        headers={"X-Session-ID": SESSION_ID},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["tipo_entrega"] == "ENVIO"
    assert data["zona_envio"] == "CABA"
    # Default cost for CABA is 3500
    assert data["costo_envio"] == "3500.00"
    assert data["pago"]["metodo"] == "TRANSFERENCIA"


@pytest.mark.asyncio
async def test_create_pedido_without_session_id(async_client_with_redis):
    """GIVEN no X-Session-ID → 400."""
    response = await async_client_with_redis.post(
        "/pedidos",
        json={
            "cliente_nombre": "Test",
            "cliente_direccion": "Test",
            "cliente_telefono": "123",
            "tipo_entrega": "RETIRO",
            "metodo_pago": "EFECTIVO",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_pedido_stock_deduction(async_client_with_redis, db_session):
    """GIVEN product with stock_kg=10.0, order quantity=2.5 → stock becomes 7.5."""
    await seed_admin(db_session)
    cat_id = await _create_category(async_client_with_redis)
    prod_id = await _create_product(async_client_with_redis, cat_id)
    await _add_to_cart(async_client_with_redis, prod_id, cantidad=2.5)

    await async_client_with_redis.post(
        "/pedidos",
        json={
            "cliente_nombre": "Test",
            "cliente_direccion": "Test",
            "cliente_telefono": "123",
            "tipo_entrega": "RETIRO",
            "metodo_pago": "EFECTIVO",
        },
        headers={"X-Session-ID": SESSION_ID},
    )

    # Check stock via productos endpoint
    resp = await async_client_with_redis.get(f"/productos/{prod_id}")
    assert resp.status_code == 200
    assert resp.json()["stock_kg"] == 7.5


# ── List / Get Pedidos (admin) ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_pedidos_admin(async_client_with_redis, db_session):
    """GIVEN orders exist + admin token → returns list."""
    await seed_admin(db_session)
    cat_id = await _create_category(async_client_with_redis)
    prod_id = await _create_product(async_client_with_redis, cat_id)
    await _add_to_cart(async_client_with_redis, prod_id, cantidad=1.0)

    await async_client_with_redis.post(
        "/pedidos",
        json={
            "cliente_nombre": "Test",
            "cliente_direccion": "Test",
            "cliente_telefono": "123",
            "tipo_entrega": "RETIRO",
            "metodo_pago": "EFECTIVO",
        },
        headers={"X-Session-ID": SESSION_ID},
    )

    headers = await _auth_headers(async_client_with_redis)
    response = await async_client_with_redis.get("/pedidos", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_pedido_by_id(async_client_with_redis, db_session):
    """GIVEN admin token → returns order detail with items and pago."""
    await seed_admin(db_session)
    cat_id = await _create_category(async_client_with_redis)
    prod_id = await _create_product(async_client_with_redis, cat_id)
    await _add_to_cart(async_client_with_redis, prod_id, cantidad=1.0)

    create_resp = await async_client_with_redis.post(
        "/pedidos",
        json={
            "cliente_nombre": "Test",
            "cliente_direccion": "Test",
            "cliente_telefono": "123",
            "tipo_entrega": "RETIRO",
            "metodo_pago": "EFECTIVO",
        },
        headers={"X-Session-ID": SESSION_ID},
    )
    pedido_id = create_resp.json()["id"]

    headers = await _auth_headers(async_client_with_redis)
    response = await async_client_with_redis.get(f"/pedidos/{pedido_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == pedido_id
    assert len(data["items"]) == 1
    assert data["pago"] is not None


@pytest.mark.asyncio
async def test_get_pedido_not_found(async_client_with_redis, db_session):
    """GIVEN admin token + nonexistent id → 404."""
    await seed_admin(db_session)
    headers = await _auth_headers(async_client_with_redis)
    response = await async_client_with_redis.get("/pedidos/9999", headers=headers)
    assert response.status_code == 404


# ── State Machine ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_state_transition_pendiente_to_confirmado(async_client_with_redis, db_session):
    """GIVEN pending order + admin → transition to confirmed."""
    await seed_admin(db_session)
    cat_id = await _create_category(async_client_with_redis)
    prod_id = await _create_product(async_client_with_redis, cat_id)
    await _add_to_cart(async_client_with_redis, prod_id, cantidad=1.0)

    create_resp = await async_client_with_redis.post(
        "/pedidos",
        json={
            "cliente_nombre": "Test",
            "cliente_direccion": "Test",
            "cliente_telefono": "123",
            "tipo_entrega": "RETIRO",
            "metodo_pago": "EFECTIVO",
        },
        headers={"X-Session-ID": SESSION_ID},
    )
    pedido_id = create_resp.json()["id"]

    headers = await _auth_headers(async_client_with_redis)
    response = await async_client_with_redis.put(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "CONFIRMADO"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "CONFIRMADO"


@pytest.mark.asyncio
async def test_state_transition_confirmado_to_entregado(async_client_with_redis, db_session):
    """GIVEN confirmed order → transition to delivered."""
    await seed_admin(db_session)
    cat_id = await _create_category(async_client_with_redis)
    prod_id = await _create_product(async_client_with_redis, cat_id)
    await _add_to_cart(async_client_with_redis, prod_id, cantidad=1.0)

    create_resp = await async_client_with_redis.post(
        "/pedidos",
        json={
            "cliente_nombre": "Test",
            "cliente_direccion": "Test",
            "cliente_telefono": "123",
            "tipo_entrega": "RETIRO",
            "metodo_pago": "EFECTIVO",
        },
        headers={"X-Session-ID": SESSION_ID},
    )
    pedido_id = create_resp.json()["id"]

    headers = await _auth_headers(async_client_with_redis)
    # Confirm first
    await async_client_with_redis.put(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "CONFIRMADO"},
        headers=headers,
    )
    # Then deliver
    response = await async_client_with_redis.put(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "ENTREGADO"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "ENTREGADO"


@pytest.mark.asyncio
async def test_state_transition_invalid(async_client_with_redis, db_session):
    """GIVEN pending order → cannot jump to ENTREGADO directly."""
    await seed_admin(db_session)
    cat_id = await _create_category(async_client_with_redis)
    prod_id = await _create_product(async_client_with_redis, cat_id)
    await _add_to_cart(async_client_with_redis, prod_id, cantidad=1.0)

    create_resp = await async_client_with_redis.post(
        "/pedidos",
        json={
            "cliente_nombre": "Test",
            "cliente_direccion": "Test",
            "cliente_telefono": "123",
            "tipo_entrega": "RETIRO",
            "metodo_pago": "EFECTIVO",
        },
        headers={"X-Session-ID": SESSION_ID},
    )
    pedido_id = create_resp.json()["id"]

    headers = await _auth_headers(async_client_with_redis)
    response = await async_client_with_redis.put(
        f"/pedidos/{pedido_id}/estado",
        json={"estado": "ENTREGADO"},
        headers=headers,
    )
    assert response.status_code == 400
    assert "Cannot transition" in response.json()["detail"]


@pytest.mark.asyncio
async def test_pedido_requires_auth(async_client_with_redis):
    """GIVEN no auth → GET /pedidos returns 401."""
    response = await async_client_with_redis.get("/pedidos")
    assert response.status_code == 401
