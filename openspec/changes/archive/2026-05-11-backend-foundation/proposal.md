# Proposal: Backend Foundation

## Intent

Backend RESTful para NutriStore: catálogo, carrito anónimo, pedidos, pagos y envíos. Headless API consumida por frontend React.

## Scope

### In Scope
- FastAPI + SQLAlchemy async + PostgreSQL + Redis (Docker)
- JWT auth admin + seeder inicial
- CRUD: productos, categorías, pedidos
- Carrito anónimo en Redis (session_id)
- POST /pedidos → crea pedido + items + limpia carrito
- GET/PUT /envios/config (admin)
- Tests por dominio en tests/

### Out of Scope
- Frontend, registro de usuarios, pasarela de pagos real
- Autenticación de clientes

## Capabilities

### New Capabilities
- `admin-auth`: JWT login, seeder admin inicial
- `categorias`: CRUD categorías
- `productos`: CRUD productos + imágenes (máx 2)
- `carrito`: Carrito Redis por session_id anónimo
- `pedidos`: Creación/consulta de pedidos + items
- `pagos`: Tracking pagos (efectivo/transferencia)
- `envios-config`: Zonas y costos de envío (admin)

### Modified Capabilities
None

## Approach

Dominios separados: `app/usuarios/`, `app/productos/`, `app/pedidos/`, `app/carrito/`. Cada uno con routers + schemas Pydantic + services. SQLAlchemy models centralizados en `app/models/`. Redis inyectado vía FastAPI dependency.

## Affected Areas

| Area | Impact |
|------|--------|
| backend/app/ | New — domains, models, routers |
| backend/tests/ | New — tests por dominio |
| backend/docker-compose.yml | New — PostgreSQL + Redis |
| backend/pyproject.toml | New — uv config |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Modelos inconsistentes con reglas de negocio | Low | Pydantic + tests de dominio |
| Race condition carrito → pedido | Low | Transacción atómica: crear pedido → limpiar carrito |
| Sin alembic para migraciones | Med | Incluir alembic setup desde el inicio |

## Rollback Plan

1. `docker compose down -v` → destruye DB + Redis
2. `git checkout` de archivos nuevos si aplica
3. Restaurar snapshot de DB si hay datos en prod

## Success Criteria

- [ ] `uv run pytest` → todos los tests pasan
- [ ] POST /auth/login → devuelve JWT válido
- [ ] CRUD productos y categorías funcional
- [ ] Carrito Redis: GET/POST + limpieza post-pedido
- [ ] POST /pedidos → pedido + items creados, carrito limpio
- [ ] GET/PUT /envios/config → endpoints protegidos por JWT
