"""Seed test products for NutriStore demo.
Safe to run multiple times — skips existing categories and products."""

import asyncio
from sqlalchemy import select
from app.database import async_session
from app.models.categoria import Categoria
from app.models.producto import Producto
from app.productos.service import create_categoria, create_producto
from app.productos.schemas import CategoriaCreate, ProductoCreate


async def get_or_create_categoria(db, data):
    result = await db.execute(select(Categoria).where(Categoria.nombre == data.nombre))
    cat = result.scalar_one_or_none()
    if cat:
        return cat
    return await create_categoria(db, data)


async def seed():
    async with async_session() as db:
        categorias_data = [
            CategoriaCreate(nombre="Granos y Legumbres", descripcion="Lentejas, porotos, garbanzos y más"),
            CategoriaCreate(nombre="Frutos Secos", descripcion="Almendras, nueces, castañas"),
            CategoriaCreate(nombre="Harinas", descripcion="Harinas integrales, de almendras, de coco"),
            CategoriaCreate(nombre="Superalimentos", descripcion="Chía, quinoa, semillas de lino"),
        ]

        cats = []
        for cat_data in categorias_data:
            cat = await get_or_create_categoria(db, cat_data)
            cats.append(cat)
            print(f"  ✅ Categoría: {cat.nombre}")

        productos_data = [
            ProductoCreate(nombre="Granola Artesanal", descripcion="Con avena, miel, frutas secas y semillas.", precio_por_kg=4200, gramos=500, tipo_unidad="KG", stock_kg=15, categoria_id=cats[0].id),
            ProductoCreate(nombre="Lentejas Secas", descripcion="Lentejas marrones seleccionadas. Ricas en hierro.", precio_por_kg=1800, gramos=1000, tipo_unidad="KG", stock_kg=25, categoria_id=cats[0].id),
            ProductoCreate(nombre="Almendras Crudas", descripcion="Almendras enteras sin sal. Fuente de vitamina E.", precio_por_kg=6500, gramos=500, tipo_unidad="KG", stock_kg=10, categoria_id=cats[1].id),
            ProductoCreate(nombre="Mix Frutos Secos", descripcion="Almendras, nueces, castañas y avellanas.", precio_por_kg=7200, gramos=500, tipo_unidad="KG", stock_kg=8, categoria_id=cats[1].id),
            ProductoCreate(nombre="Harina de Almendras", descripcion="Ideal para preparaciones sin TACC.", precio_por_kg=5800, gramos=500, tipo_unidad="KG", stock_kg=6, categoria_id=cats[2].id),
            ProductoCreate(nombre="Harina Integral Orgánica", descripcion="Harina de trigo integral molida a piedra.", precio_por_kg=1500, gramos=1000, tipo_unidad="KG", stock_kg=30, categoria_id=cats[2].id),
            ProductoCreate(nombre="Semillas de Chía", descripcion="Chía orgánica nacional. Rica en omega 3.", precio_por_kg=4500, gramos=500, tipo_unidad="KG", stock_kg=12, categoria_id=cats[3].id),
            ProductoCreate(nombre="Quinoa Real", descripcion="Quinoa real boliviana. Proteína completa.", precio_por_kg=3800, gramos=500, tipo_unidad="KG", stock_kg=10, categoria_id=cats[3].id),
            ProductoCreate(nombre="Barrita de Cereal", descripcion="Avena y miel. Snack saludable.", precio_por_kg=0, precio_por_unidad=450, tipo_unidad="UNIDAD", stock_unidades=50, categoria_id=cats[3].id),
            ProductoCreate(nombre="Aceite de Coco", descripcion="Extra virgen prensado en frío.", precio_por_kg=3800, gramos=500, tipo_unidad="KG", stock_kg=8, categoria_id=cats[3].id),
        ]

        created = 0
        for prod_data in productos_data:
            result = await db.execute(select(Producto).where(Producto.nombre == prod_data.nombre))
            if result.scalar_one_or_none():
                print(f"  ➡️ Ya existe: {prod_data.nombre}")
                continue
            prod = await create_producto(db, prod_data)
            created += 1
            unidad = f"{prod.gramos}g" if prod.tipo_unidad.value == "KG" else "unidad"
            precio = prod.precio_por_kg if prod.tipo_unidad.value == "KG" else prod.precio_por_unidad
            print(f"  ✅ {prod.nombre} — ${precio} / {unidad}")

        print(f"\n🎉 {created} productos nuevos (sobre {len(productos_data)} totales)")


if __name__ == "__main__":
    asyncio.run(seed())
