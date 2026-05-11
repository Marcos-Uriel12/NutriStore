from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
    import traceback
    try:
        from app.usuarios.service import seed_admin
        async with async_session() as session:
            await seed_admin(session)
        app.state.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        print("✅ Startup OK")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        traceback.print_exc()
        raise
    try:
        yield
    finally:
        await app.state.redis.close()

# CORS for frontend deployed separately
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios_router, prefix="/auth", tags=["Auth"])
app.include_router(categorias_router, prefix="/categorias", tags=["Categorias"])
app.include_router(productos_router, prefix="/productos", tags=["Productos"])
app.include_router(carrito_router, prefix="/carrito", tags=["Carrito"])
app.include_router(pedidos_router, prefix="/pedidos", tags=["Pedidos"])
app.include_router(envios_router, prefix="/envios", tags=["Envios"])

# Mount frontend as static files — must be AFTER all API routers
_frontend_path = Path(__file__).resolve().parent.parent.parent / "frontend"
if _frontend_path.is_dir():
    app.mount("/", StaticFiles(directory=str(_frontend_path), html=True), name="frontend")
