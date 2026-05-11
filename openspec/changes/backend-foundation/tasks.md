# Tasks: Backend Foundation

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~2000–2500 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR #1 Infra+Models → PR #2 Auth+CRUD → PR #3 Cart+Orders+Shipping |
| Delivery strategy | auto-chain |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Infra + Models + Alembic | PR #1 | Base = feature/tracker branch. Docker, config, DB, models, migration, model tests |
| 2 | Auth + Categories + Products CRUD | PR #2 | Base = PR #1 branch. Depends on models from PR #1. Includes domain tests |
| 3 | Cart + Orders + Payments + Shipping | PR #3 | Base = PR #2 branch. Depends on auth guard + productos from PR #2. Includes tests |

## PR #1: Infrastructure + Models + Alembic

### Phase 1: Foundation

- [x] 1.1 Create `docker-compose.yml` (PostgreSQL 16 + Redis 7)
- [x] 1.2 Create `Dockerfile` (Python 3.12-slim, uv)
- [x] 1.3 Create `pyproject.toml` with all deps (fastapi, sqlalchemy, asyncpg, redis, alembic, jose, passlib, pytest, httpx, fakeredis, aiosqlite)
- [x] 1.4 Create `app/__init__.py`
- [x] 1.5 Create `app/config.py` (Pydantic Settings)
- [x] 1.6 Create `app/database.py` (async_engine, sessionmaker, get_db)

### Phase 2: Models + Alembic

- [x] 2.1 Create `app/models/__init__.py`
- [x] 2.2 Create `app/models/admin.py` (Admin)
- [x] 2.3 Create `app/models/categoria.py` (Categoria)
- [x] 2.4 Create `app/models/producto.py` (Producto, TipoUnidad enum)
- [x] 2.5 Create `app/models/imagen.py` (Imagen)
- [x] 2.6 Create `app/models/pedido.py` (Pedido, estado enum)
- [x] 2.7 Create `app/models/pedido_item.py` (PedidoItem)
- [x] 2.8 Create `app/models/pago.py` (Pago)
- [x] 2.9 Create `app/models/envio.py` (EnvioConfig, zonas JSON)
- [x] 2.10 Create `alembic.ini` + `alembic/env.py`
- [x] 2.11 Run `alembic revision --autogenerate` → first migration

### Phase 3: Model Tests

- [x] 3.1 Create `tests/conftest.py` (async SQLite, TestClient, fixtures)
- [x] 3.2 Write model tests: Admin hash, TipoUnidad enum, Pedido state defaults
- [x] 3.3 Verify `alembic upgrade head` creates all tables

## PR #2: Auth + CRUD (High-level)

- [x] 4.1 Create `app/dependencies.py` (JWT guard, get_redis)
- [x] 4.2 Create `app/usuarios/` (router, schemas, service) — login + me
- [x] 4.3 Create `app/productos/` — categorias + productos + imágenes
- [x] 4.4 Create `app/main.py` (app, lifespan, routers, seeder)
- [x] 4.5 Create `scripts/seed.py`
- [x] 4.6 Write tests: test_auth.py, test_productos.py

## PR #3: Cart + Orders + Shipping (High-level)

- [ ] 5.1 Create `app/carrito/` (Redis cart by session_id)
- [ ] 5.2 Create `app/pedidos/` (state machine, cart→order atomically)
- [ ] 5.3 Create `app/envios/` (zones + costs, admin-only)
- [ ] 5.4 Write tests: carrito (fakeredis), pedidos, pagos, envios
