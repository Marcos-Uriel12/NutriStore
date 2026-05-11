from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categoria import Categoria
from app.models.imagen import Imagen
from app.models.producto import Producto
from app.productos.schemas import (
    CategoriaCreate,
    ProductoCreate,
    ProductoUpdate,
)


# ── Categorias ────────────────────────────────────────────────────────


async def create_categoria(db: AsyncSession, data: CategoriaCreate) -> Categoria:
    categoria = Categoria(nombre=data.nombre, descripcion=data.descripcion)
    db.add(categoria)
    await db.commit()
    await db.refresh(categoria)
    return categoria


async def list_categorias(db: AsyncSession) -> list[Categoria]:
    result = await db.execute(select(Categoria).order_by(Categoria.nombre))
    return list(result.scalars().all())


async def categoria_exists_by_name(db: AsyncSession, nombre: str) -> bool:
    result = await db.execute(
        select(func.count()).select_from(Categoria).where(Categoria.nombre == nombre)
    )
    count = result.scalar()
    return count is not None and count > 0


# ── Productos ──────────────────────────────────────────────────────────


async def create_producto(db: AsyncSession, data: ProductoCreate) -> Producto:
    producto = Producto(
        nombre=data.nombre,
        descripcion=data.descripcion,
        precio_por_kg=data.precio_por_kg,
        precio_por_unidad=data.precio_por_unidad,
        tipo_unidad=data.tipo_unidad,
        stock_kg=data.stock_kg,
        stock_unidades=data.stock_unidades,
        categoria_id=data.categoria_id,
    )
    for img in data.imagenes:
        producto.imagenes.append(Imagen(url=img.url))

    db.add(producto)
    await db.commit()
    await db.refresh(producto)
    return producto


async def list_productos(db: AsyncSession) -> list[Producto]:
    result = await db.execute(
        select(Producto).where(Producto.activo == True).order_by(Producto.nombre)
    )
    return list(result.scalars().all())


async def get_producto(db: AsyncSession, producto_id: int) -> Producto | None:
    result = await db.execute(select(Producto).where(Producto.id == producto_id))
    return result.scalar_one_or_none()


async def update_producto(
    db: AsyncSession, producto: Producto, data: ProductoUpdate
) -> Producto:
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(producto, key, value)
    await db.commit()
    await db.refresh(producto)
    return producto


async def soft_delete_producto(db: AsyncSession, producto: Producto) -> Producto:
    producto.activo = False
    await db.commit()
    await db.refresh(producto)
    return producto
