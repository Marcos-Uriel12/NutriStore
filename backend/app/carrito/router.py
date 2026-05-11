from fastapi import APIRouter, Depends, Header, HTTPException, status
from redis.asyncio import Redis

from app.carrito.schemas import CartItemCreate, CartItemResponse
from app.carrito import service as cart_service
from app.dependencies import get_redis

router = APIRouter()


@router.get("", response_model=list[CartItemResponse])
async def get_cart(
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
    redis: Redis = Depends(get_redis),
):
    if not x_session_id:
        return []
    return await cart_service.get_cart(redis, x_session_id)


@router.post("", response_model=list[CartItemResponse], status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item: CartItemCreate,
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
    redis: Redis = Depends(get_redis),
):
    if not x_session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Session-ID header is required",
        )
    await cart_service.add_to_cart(redis, x_session_id, item)
    return await cart_service.get_cart(redis, x_session_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    x_session_id: str | None = Header(None, alias="X-Session-ID"),
    redis: Redis = Depends(get_redis),
):
    if x_session_id:
        await cart_service.clear_cart(redis, x_session_id)
