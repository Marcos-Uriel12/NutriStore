from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.admin import Admin
from app.productos.schemas import (
    CategoriaCreate,
    CategoriaResponse,
    ProductoCreate,
    ProductoResponse,
    ProductoUpdate,
)
from app.productos import service as productos_service

categorias_router = APIRouter()
productos_router = APIRouter()


# ── Categorias ──────────────────────────────────────────────────────────


@categorias_router.get("", response_model=list[CategoriaResponse])
async def list_categorias(db: AsyncSession = Depends(get_db)):
    return await productos_service.list_categorias(db)


@categorias_router.post("", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def create_categoria(
    data: CategoriaCreate,
    db: AsyncSession = Depends(get_db),
    _admin: Admin = Depends(get_current_admin),
):
    if await productos_service.categoria_exists_by_name(db, data.nombre):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Categoria already exists",
        )
    return await productos_service.create_categoria(db, data)


# ── Productos ───────────────────────────────────────────────────────────


@productos_router.get("", response_model=list[ProductoResponse])
async def list_productos(db: AsyncSession = Depends(get_db)):
    return await productos_service.list_productos(db)


@productos_router.get("/{producto_id}", response_model=ProductoResponse)
async def get_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    producto = await productos_service.get_producto(db, producto_id)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto not found")
    return producto


@productos_router.post("", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def create_producto(
    data: ProductoCreate,
    db: AsyncSession = Depends(get_db),
    _admin: Admin = Depends(get_current_admin),
):
    return await productos_service.create_producto(db, data)


@productos_router.put("/{producto_id}", response_model=ProductoResponse)
async def update_producto(
    producto_id: int,
    data: ProductoUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: Admin = Depends(get_current_admin),
):
    producto = await productos_service.get_producto(db, producto_id)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto not found")
    return await productos_service.update_producto(db, producto, data)


@productos_router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_producto(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: Admin = Depends(get_current_admin),
):
    producto = await productos_service.get_producto(db, producto_id)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto not found")
    await productos_service.soft_delete_producto(db, producto)
