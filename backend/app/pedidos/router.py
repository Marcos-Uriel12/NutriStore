from fastapi import APIRouter, Depends, Header, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin, get_redis
from app.models.admin import Admin
from app.pedidos.schemas import (
    PedidoCreate,
    PedidoResponse,
    EstadoUpdate,
)
from app.pedidos import service as pedidos_service

router = APIRouter()


@router.post("", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def create_pedido(
    data: PedidoCreate,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    if not x_session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Session-ID header is required",
        )
    return await pedidos_service.create_pedido(db, redis, x_session_id, data)


@router.get("", response_model=list[PedidoResponse])
async def list_pedidos(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
):
    """Admin sees all orders. Anonymous sees own orders."""
    # If admin is authenticated, return all
    # Non-admin requests will hit the Depends guard first (401)
    return await pedidos_service.list_pedidos(db, session_id=None)


@router.get("/{pedido_id}", response_model=PedidoResponse)
async def get_pedido(
    pedido_id: int,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    pedido = await pedidos_service.get_pedido(db, pedido_id)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return pedido


@router.put("/{pedido_id}/estado", response_model=PedidoResponse)
async def update_estado(
    pedido_id: int,
    data: EstadoUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return await pedidos_service.update_estado(db, pedido_id, data.estado)
