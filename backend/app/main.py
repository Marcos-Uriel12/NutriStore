from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import async_session
from app.usuarios.router import router as usuarios_router
from app.productos.router import categorias_router, productos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed admin on startup (idempotent)
    from app.usuarios.service import seed_admin

    async with async_session() as session:
        await seed_admin(session)
    yield


app = FastAPI(title="NutriStore API", lifespan=lifespan)

app.include_router(usuarios_router, prefix="/auth", tags=["Auth"])
app.include_router(categorias_router, prefix="/categorias", tags=["Categorias"])
app.include_router(productos_router, prefix="/productos", tags=["Productos"])
