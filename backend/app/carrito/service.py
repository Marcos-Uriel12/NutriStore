import json

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
    db: AsyncSession | None = None,
) -> list[CartItemResponse]:
    """Return all items in the cart, optionally enriched with product info."""
    raw = await redis.hgetall(_cart_key(session_id))
    items: list[CartItemResponse] = []
    for pid, data in raw.items():
        parsed = json.loads(data)
        items.append(CartItemResponse(
            producto_id=int(pid),
            cantidad=parsed["cantidad"],
            unidad_medida=UnidadMedida(parsed["unidad_medida"]),
        ))

    # Enrich with product info if db is available and items exist
    if db and items:
        from app.models.producto import Producto

        producto_ids = [i.producto_id for i in items]
        result = await db.execute(select(Producto).where(Producto.id.in_(producto_ids)))
        productos = {p.id: p for p in result.scalars().all()}

        for item in items:
            prod = productos.get(item.producto_id)
            if prod:
                item.nombre = prod.nombre
                if prod.tipo_unidad.value == "KG":
                    item.precio = float(prod.precio_por_kg)
                else:
                    item.precio = float(prod.precio_por_unidad or 0)
                item.imagen_url = prod.imagenes[0].url if prod.imagenes else ""
                item.tipo_unidad = prod.tipo_unidad.value

    return items


async def clear_cart(redis: Redis, session_id: str) -> None:
    """Delete the cart key."""
    await redis.delete(_cart_key(session_id))
