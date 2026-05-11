import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.admin import Admin
from app.models.producto import Producto
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


@productos_router.get("/page", response_class=HTMLResponse)
async def productos_page(
    p: int = Query(1, ge=1),
    limit: int = Query(8, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Return Bootstrap product cards as HTML fragment for HTMX infinite scroll."""
    offset = (p - 1) * limit
    result = await db.execute(
        select(Producto)
        .where(Producto.activo == True)
        .offset(offset)
        .limit(limit + 1)
        .order_by(Producto.nombre)
    )
    productos = result.scalars().all()
    has_next = len(productos) > limit
    productos = productos[:limit]

    cards_html = ""
    for prod in productos:
        img_url = prod.imagenes[0].url if prod.imagenes else "/img/placeholder.svg"
        if prod.tipo_unidad.value == "KG":
            precio = f"${prod.precio_por_kg:.2f} / {prod.gramos}g"
        else:
            precio = f"${prod.precio_por_unidad:.2f}" if prod.precio_por_unidad else ""

        cards_html += f"""
        <div class="col-md-3 col-6 mb-4">
            <div class="card product-card h-100">
                <img src="{img_url}" class="card-img-top" alt="{prod.nombre}" loading="lazy">
                <div class="card-body">
                    <h6 class="card-title">{prod.nombre}</h6>
                    <p class="card-text text-muted small">{precio}</p>
                    <button class="btn btn-sm btn-primary add-to-cart"
                            data-producto-id="{prod.id}"
                            data-nombre="{prod.nombre}"
                            data-precio="{precio}">
                        Agregar
                    </button>
                </div>
            </div>
        </div>"""

    if has_next:
        cards_html += f"""<div class="col-12 text-center py-3"
            hx-get="/productos/page?p={p + 1}&limit={limit}"
            hx-trigger="revealed"
            hx-swap="outerHTML"
            hx-target="this">
            <div class="spinner-border text-success" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </div>"""
    else:
        cards_html += '<div class="col-12 text-center py-3 text-muted"><small>No hay más productos</small></div>'

    return cards_html


UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "img" / "uploads"


@productos_router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_product_image(
    file: UploadFile = File(...),
    _admin: Admin = Depends(get_current_admin),
):
    """Upload a product image file. Returns the URL path."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename or ".jpg")[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        raise HTTPException(status_code=400, detail="Formato no soportado. Usá JPG, PNG, WEBP o GIF.")

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    return {"url": f"/img/uploads/{filename}"}


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
