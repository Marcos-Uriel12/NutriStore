# Design: Backend Foundation

## Technical Approach

Domain-organized FastAPI monolith with centralized models, async SQLAlchemy + PostgreSQL, Redis for anonymous cart, and JWT auth for admin. Each domain (usuarios, productos, carrito, pedidos, envios) gets its own `router.py`, `schemas.py`, and `service.py`. Tests per domain under `tests/`.

---

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|-------------|-----------|
| **SQLAlchemy async** | `async_sessionmaker` + `AsyncSession` | Sync SQLAlchemy, Tortoise-ORM | Async avoids blocking on I/O; SQLAlchemy 2.0 async pattern is mature and well-integrated with FastAPI |
| **Redis client** | `redis-py` asyncio via lifespan | `aioredis` (deprecated) | `redis-py` 4.x+ absorbed aioredis; lifespan context manager ensures clean connect/disconnect |
| **JWT auth** | `OAuth2PasswordBearer` + `python-jose` | FastAPI's built-in OAuth2, django-cookiecutter | Lightweight, no framework lock-in; token expiry via env config; middleware via `Depends()` |
| **Unit of measure** | Enum `TipoUnidad(KG \| UNIDAD)` | Separate tables per type | Simple, type-safe, single column check on `producto` |
| **Pedido state machine** | Enum transitions in service layer | State machine library | Only 4 states with 3 transitions; no need for external lib. Validated in `pedido/service.py` |
| **Cart → Order flow** | DB transaction + Redis flush at end | Two-phase commit | Single transaction: create `Pedido` + `PedidoItem` + `Pago`, then flush Redis. If anything fails, no data written |
| **Alembic** | Auto-generate first migration from models | Manual DDL | Keeps schema versioned from day one; `alembic revision --autogenerate` after models are defined |
| **Seeder** | Startup event checks admin count | Separate CLI script | Run on every startup; idempotent — checks `Admin.count()` before inserting |

---

## Data Flow

```
           ┌──────────┐
           │  Client   │
           └─────┬─────┘
                 │ session_id (Cookie)
                 ▼
┌────────────────────────────────────┐
│          FastAPI App               │
│                                    │
│  /auth/*    → usuarios/ (JWT)      │
│  /categorias → productos/ (CRUD)   │
│  /productos  → productos/ (CRUD)   │
│  /carrito/*  → carrito/ (Redis)    │
│  /pedidos/*  → pedidos/ (DB+Redis) │
│  /envios/*   → envios/ (config)    │
└────────┬───────────────────┬───────┘
         │                  │
         ▼                  ▼
    ┌─────────┐      ┌──────────┐
    │PostgreSQL│      │  Redis   │
    │ (models) │      │ (cart:* )│
    └─────────┘      └──────────┘
```

**Cart → Order transaction sequence:**
```
POST /pedidos
  1. Read cart: REDIS GET cart:{session_id}
  2. Validate stock for each item
  3. DB BEGIN
  4.   INSERT pedido, pedido_items, pago
  5.   UPDATE producto.stock (deduct)
  6. DB COMMIT
  7. REDIS DEL cart:{session_id}
  8. Return PedidoResponse
```

---

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/docker-compose.yml` | Create | PostgreSQL 16 + Redis 7, volumes, healthchecks |
| `backend/Dockerfile` | Create | Python 3.12 slim, uv install |
| `backend/pyproject.toml` | Create | uv project deps: fastapi, sqlalchemy, asyncpg, redis, alembic, jose, passlib, pytest, httpx |
| `backend/alembic.ini` | Create | Migration config |
| `backend/alembic/env.py` | Create | Async Alembic env, target metadata |
| `backend/alembic/versions/.gitkeep` | Create | Placeholder for first migration |
| `backend/app/__init__.py` | Create | Package init |
| `backend/app/main.py` | Create | FastAPI app, lifespan (Redis + seeder), include routers |
| `backend/app/config.py` | Create | Pydantic Settings from env vars |
| `backend/app/database.py` | Create | `async_engine`, `async_sessionmaker`, `get_db` dependency |
| `backend/app/dependencies.py` | Create | `get_current_admin` JWT guard, `get_redis` |
| `backend/app/models/__init__.py` | Create | Re-export all models |
| `backend/app/models/admin.py` | Create | Admin model (id, email, hashed_password, created_at) |
| `backend/app/models/categoria.py` | Create | Categoria model (id, nombre, descripcion) |
| `backend/app/models/producto.py` | Create | Producto model (id, nombre, categoria_id, precio, tipo_unidad, stock, imagenes[]) |
| `backend/app/models/imagen.py` | Create | Imagen model (id, producto_id, url, orden) |
| `backend/app/models/pedido.py` | Create | Pedido model (id, session_id, estado, tipo_entrega, zona_envio, costo_envio, nombre, direccion, telefono, created_at) |
| `backend/app/models/pedido_item.py` | Create | PedidoItem model (id, pedido_id, producto_id, cantidad, precio_unitario) |
| `backend/app/models/pago.py` | Create | Pago model (id, pedido_id, metodo, estado) |
| `backend/app/models/envio.py` | Create | EnvioConfig model (id, zonas JSON) |
| `backend/app/usuarios/` | Create | router (POST /auth/login, GET /auth/me), schemas, service |
| `backend/app/productos/` | Create | router (CRUD categorías + productos), schemas, service |
| `backend/app/carrito/` | Create | router (GET/POST/DELETE /carrito), schemas, service (Redis ops) |
| `backend/app/pedidos/` | Create | router (POST /pedidos, PUT estado), schemas, service (state machine) |
| `backend/app/envios/` | Create | router (GET/PUT /envios/config), schemas, service |
| `backend/tests/` | Create | conftest.py (test DB, async client fixtures), 6 test files |
| `backend/scripts/seed.py` | Create | CLI to create admin (email/password from env) |

---

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| **Unit (services)** | Stock deduction logic, state machine transitions, JWT encode/decode | Mock DB session/Redis; test pure business logic |
| **Integration (routers)** | Full endpoint flows via HTTP | `httpx.AsyncClient` with FastAPI `TestClient`; async SQLite as test DB (fast, isolated per test) |
| **Cart** | Redis CRUD, upsert, flush | `fakeredis` async — fast, no external dependency |
| **Auth** | 200/401, protected routes | `Depends(get_current_admin)` tests with valid + expired + missing tokens |

**Test DB decision:** Use async SQLite (`aiosqlite`) for tests. SQLAlchemy 2.0 async engine abstracts the driver; tests run &sdot;10× faster than spinning a Postgres container per test run. Accept risk of dialect-specific features (Postgres JSON, enums) by testing those explicitly via integration against a real Postgres in CI.

---

## Migration / Rollout

No migration required — greenfield project. First deploy: `alembic upgrade head` creates all tables. Seeder creates admin on first request.

---

## Open Questions

- [ ] Confirm test DB strategy: async SQLite for speed vs. Postgres container for fidelity?
