from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from app.config import settings
from app.database import async_session
from app.usuarios.router import router as usuarios_router
from app.productos.router import categorias_router, productos_router
from app.carrito.router import router as carrito_router
from app.pedidos.router import router as pedidos_router
from app.envios.router import router as envios_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed admin on startup (idempotent)
    from app.usuarios.service import seed_admin

    async with async_session() as session:
        await seed_admin(session)

    # Redis for anonymous cart (managed by lifespan)
    app.state.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield
    finally:
        await app.state.redis.close()


app = FastAPI(title="NutriStore API", lifespan=lifespan)

app.include_router(usuarios_router, prefix="/auth", tags=["Auth"])
app.include_router(categorias_router, prefix="/categorias", tags=["Categorias"])
app.include_router(productos_router, prefix="/productos", tags=["Productos"])
app.include_router(carrito_router, prefix="/carrito", tags=["Carrito"])
app.include_router(pedidos_router, prefix="/pedidos", tags=["Pedidos"])
app.include_router(envios_router, prefix="/envios", tags=["Envios"])
