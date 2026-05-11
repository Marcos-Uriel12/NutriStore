"""Integration tests for carrito (Redis cart) endpoints."""

import pytest


SESSION_ID = "test-session-abc123"


@pytest.mark.asyncio
async def test_get_empty_cart(async_client_with_redis):
    """GIVEN no items in cart → empty array."""
    response = await async_client_with_redis.get(
        "/carrito",
        headers={"X-Session-ID": SESSION_ID},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_add_to_cart(async_client_with_redis):
    """GIVEN new producto_id → item added to cart."""
    response = await async_client_with_redis.post(
        "/carrito",
        json={"producto_id": 1, "cantidad": 2.0, "unidad_medida": "KG"},
        headers={"X-Session-ID": SESSION_ID},
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["producto_id"] == 1
    assert data[0]["cantidad"] == 2.0
    assert data[0]["unidad_medida"] == "KG"


@pytest.mark.asyncio
async def test_add_update_item(async_client_with_redis):
    """GIVEN existing producto_id → quantity updated."""
    headers = {"X-Session-ID": SESSION_ID}
    # Add first
    await async_client_with_redis.post(
        "/carrito",
        json={"producto_id": 1, "cantidad": 2.0, "unidad_medida": "KG"},
        headers=headers,
    )
    # Update same product
    response = await async_client_with_redis.post(
        "/carrito",
        json={"producto_id": 1, "cantidad": 5.0, "unidad_medida": "KG"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["cantidad"] == 5.0


@pytest.mark.asyncio
async def test_clear_cart(async_client_with_redis):
    """GIVEN items in cart → DELETE clears it."""
    headers = {"X-Session-ID": SESSION_ID}
    await async_client_with_redis.post(
        "/carrito",
        json={"producto_id": 1, "cantidad": 3.0, "unidad_medida": "KG"},
        headers=headers,
    )

    response = await async_client_with_redis.delete("/carrito", headers=headers)
    assert response.status_code == 204

    # Verify empty
    get_resp = await async_client_with_redis.get("/carrito", headers=headers)
    assert get_resp.json() == []


@pytest.mark.asyncio
async def test_add_without_session_id(async_client_with_redis):
    """GIVEN no X-Session-ID header → 400."""
    response = await async_client_with_redis.post(
        "/carrito",
        json={"producto_id": 1, "cantidad": 1.0, "unidad_medida": "KG"},
    )
    assert response.status_code == 400
    assert "X-Session-ID" in response.json()["detail"]


@pytest.mark.asyncio
async def test_multiple_items(async_client_with_redis):
    """GIVEN two different products in cart → both listed."""
    headers = {"X-Session-ID": SESSION_ID}
    await async_client_with_redis.post(
        "/carrito",
        json={"producto_id": 1, "cantidad": 2.0, "unidad_medida": "KG"},
        headers=headers,
    )
    await async_client_with_redis.post(
        "/carrito",
        json={"producto_id": 2, "cantidad": 3.0, "unidad_medida": "UNIDAD"},
        headers=headers,
    )

    response = await async_client_with_redis.get("/carrito", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    product_ids = {item["producto_id"] for item in data}
    assert product_ids == {1, 2}


@pytest.mark.asyncio
async def test_default_unit_is_kg(async_client_with_redis):
    """GIVEN no unidad_medida in request → defaults to KG."""
    headers = {"X-Session-ID": SESSION_ID}
    response = await async_client_with_redis.post(
        "/carrito",
        json={"producto_id": 1, "cantidad": 1.5},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data[0]["unidad_medida"] == "KG"
