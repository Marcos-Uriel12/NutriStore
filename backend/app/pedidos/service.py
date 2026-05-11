import json
from decimal import Decimal

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.envio import EnvioConfig
from app.models.pago import Pago, EstadoPago
from app.models.pedido import (
    Pedido,
    EstadoPedido,
    TipoEntrega,
)
from app.models.pedido_item import PedidoItem
from app.models.producto import Producto
from app.pedidos.schemas import PedidoCreate

VALID_TRANSITIONS: dict[EstadoPedido, list[EstadoPedido]] = {
    EstadoPedido.PENDIENTE: [EstadoPedido.CONFIRMADO, EstadoPedido.CANCELADO],
    EstadoPedido.CONFIRMADO: [EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO],
    EstadoPedido.ENTREGADO: [],
    EstadoPedido.CANCELADO: [],
}

RETIRO_KEYWORD = "retiro-local"


async def create_pedido(
    db: AsyncSession,
    redis: Redis,
    session_id: str,
    data: PedidoCreate,
) -> Pedido:
    # 1. Read cart from Redis
    raw_cart = await redis.hgetall(f"cart:{session_id}")
    if not raw_cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty cart — add items before creating an order",
        )

    # 2. Parse and validate cart items
    cart_items: list[tuple[int, float, str]] = []  # (producto_id, cantidad, unidad_medida)
    for pid_str, item_json in raw_cart.items():
        item_data = json.loads(item_json)
        cart_items.append((
            int(pid_str),
            float(item_data["cantidad"]),
            item_data["unidad_medida"],
        ))

    # 3. Load products and validate
    producto_ids = [pid for pid, _, _ in cart_items]
    result = await db.execute(select(Producto).where(Producto.id.in_(producto_ids)))
    productos = {p.id: p for p in result.scalars().all()}

    items_data: list[dict] = []
    total = Decimal("0.00")

    for pid, cantidad, unidad_medida in cart_items:
        producto = productos.get(pid)
        if producto is None or not producto.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {pid} not found or inactive",
            )

        # Calculate price
        if unidad_medida == "KG":
            precio_unitario = producto.precio_por_kg
        else:
            if producto.precio_por_unidad is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {pid} does not have a unit price",
                )
            precio_unitario = producto.precio_por_unidad

        # Check and deduct stock
        if unidad_medida == "KG":
            if producto.stock_kg is None or producto.stock_kg < cantidad:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Insufficient stock for product {pid}",
                )
            producto.stock_kg -= cantidad
        else:
            stock_int = int(cantidad) if cantidad == int(cantidad) else None
            if stock_int is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unit quantity for product {pid} must be a whole number",
                )
            if producto.stock_unidades is None or producto.stock_unidades < stock_int:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Insufficient stock for product {pid}",
                )
            producto.stock_unidades -= stock_int

        subtotal = precio_unitario * Decimal(str(cantidad))
        total += subtotal

        items_data.append({
            "producto_id": pid,
            "cantidad": cantidad,
            "unidad_medida": unidad_medida,
            "precio_unitario": precio_unitario,
        })

    # 4. Calculate delivery cost
    if data.tipo_entrega == TipoEntrega.ENVIO and data.zona_envio:
        result = await db.execute(
            select(EnvioConfig).where(EnvioConfig.zona == data.zona_envio)
        )
        config = result.scalar_one_or_none()
        if config:
            costo_envio = config.costo
        else:
            # Fallback to defaults if DB has no config yet
            from app.envios.service import DEFAULT_COSTS
            costo_envio = DEFAULT_COSTS.get(data.zona_envio, Decimal("0.00"))
    else:
        costo_envio = Decimal("0.00")

    total += costo_envio

    # 5. Resolve delivery address
    direccion_entrega = data.direccion_entrega or (
        RETIRO_KEYWORD if data.tipo_entrega == TipoEntrega.RETIRO else data.cliente_direccion
    )

    # 6. Create pedido + items + pago in transaction
    pedido = Pedido(
        session_id=session_id,
        cliente_nombre=data.cliente_nombre,
        cliente_direccion=data.cliente_direccion,
        cliente_telefono=data.cliente_telefono,
        direccion_entrega=direccion_entrega,
        tipo_entrega=data.tipo_entrega,
        zona_envio=data.zona_envio if data.tipo_entrega == TipoEntrega.ENVIO else None,
        costo_envio=costo_envio,
        total=total,
    )
    db.add(pedido)
    await db.flush()  # get pedido.id

    for item_data in items_data:
        item = PedidoItem(
            pedido_id=pedido.id,
            producto_id=item_data["producto_id"],
            cantidad=item_data["cantidad"],
            unidad_medida=item_data["unidad_medida"],
            precio_unitario=item_data["precio_unitario"],
        )
        db.add(item)

    pago = Pago(
        pedido_id=pedido.id,
        metodo=data.metodo_pago,
        monto=total,
        estado=EstadoPago.PENDIENTE,
    )
    db.add(pago)

    await db.commit()
    await db.refresh(pedido)

    # 7. Clear Redis cart
    await redis.delete(f"cart:{session_id}")

    return pedido


async def list_pedidos(
    db: AsyncSession,
    session_id: str | None = None,
) -> list[Pedido]:
    """List orders: admin sees all, anonymous sees own."""
    stmt = (
        select(Pedido)
        .options(
            selectinload(Pedido.items).selectinload(PedidoItem.producto),
            selectinload(Pedido.pago),
        )
        .order_by(Pedido.created_at.desc())
    )
    if session_id:
        stmt = stmt.where(Pedido.session_id == session_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_pedido(db: AsyncSession, pedido_id: int) -> Pedido | None:
    result = await db.execute(
        select(Pedido)
        .options(
            selectinload(Pedido.items).selectinload(PedidoItem.producto),
            selectinload(Pedido.pago),
        )
        .where(Pedido.id == pedido_id)
    )
    return result.scalar_one_or_none()


async def update_estado(
    db: AsyncSession,
    pedido_id: int,
    nuevo_estado: EstadoPedido,
) -> Pedido:
    pedido = await get_pedido(db, pedido_id)
    if pedido is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    allowed = VALID_TRANSITIONS.get(pedido.estado, [])
    if nuevo_estado not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {pedido.estado.value} to {nuevo_estado.value}",
        )

    pedido.estado = nuevo_estado
    await db.commit()
    await db.refresh(pedido)
    return pedido
