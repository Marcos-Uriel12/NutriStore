import json

from redis.asyncio import Redis

from app.carrito.schemas import CartItemCreate, CartItemResponse
from app.models.pedido_item import UnidadMedida

CART_PREFIX = "cart:"


def _cart_key(session_id: str) -> str:
    return f"{CART_PREFIX}{session_id}"


async def add_to_cart(
    redis: Redis,
    session_id: str,
    item: CartItemCreate,
) -> None:
    """Add or update an item in the cart."""
    value = json.dumps({
        "cantidad": item.cantidad,
        "unidad_medida": item.unidad_medida.value,
    })
    await redis.hset(_cart_key(session_id), str(item.producto_id), value)


async def get_cart(
    redis: Redis,
    session_id: str,
) -> list[CartItemResponse]:
    """Return all items in the cart."""
    raw = await redis.hgetall(_cart_key(session_id))
    items: list[CartItemResponse] = []
    for pid, data in raw.items():
        parsed = json.loads(data)
        items.append(CartItemResponse(
            producto_id=int(pid),
            cantidad=parsed["cantidad"],
            unidad_medida=UnidadMedida(parsed["unidad_medida"]),
        ))
    return items


async def clear_cart(redis: Redis, session_id: str) -> None:
    """Delete the cart key."""
    await redis.delete(_cart_key(session_id))
