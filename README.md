# 🌿 NutriStore

Sistema de gestión para dietética — backend API + frontend web.

## Stack

### Backend
- **Python 3.12** + **FastAPI** (async)
- **SQLAlchemy 2.0** (async) + **PostgreSQL 16**
- **Redis 7** (carrito anónimo)
- **Alembic** (migraciones)
- **JWT** (autenticación admin)
- **Pydantic v2** (schemas)

### Frontend
- **Bootstrap 5** + **HTMX**
- **CSS custom** (tema natural verde/beige)
- Vanilla JS (carrito, admin)

### DevOps
- **Docker Compose** (PostgreSQL + Redis)
- **uv** (gestor de paquetes Python)
- **pytest** + httpx + fakeredis (tests)

## Quick Start

```bash
# 1. Clonar
git clone https://github.com/Marcos-Uriel12/NutriStore.git
cd NutriStore

# 2. Backend
cd backend
cp .env.example .env        # Configurar variables
uv sync                     # Instalar dependencias

# 3. Docker (PostgreSQL + Redis)
docker compose up -d

# 4. Migraciones
uv run alembic upgrade head

# 5. Iniciar
uv run uvicorn app.main:app --reload

# 6. Abrir
open http://localhost:8000       # Landing
open http://localhost:8000/admin/login.html  # Admin
```

## Estructura

```
backend/
├── app/
│   ├── main.py              # FastAPI app + routers
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # Async SQLAlchemy
│   ├── dependencies.py      # JWT guard + Redis
│   ├── email_service.py     # Notificaciones email
│   ├── models/              # SQLAlchemy models
│   ├── usuarios/            # Admin auth
│   ├── productos/           # CRUD productos/categorías
│   ├── carrito/             # Carrito Redis
│   ├── pedidos/             # Pedidos + pagos
│   └── envios/              # Config envíos
├── alembic/                 # Migraciones
├── tests/                   # 67 tests (pytest)
└── docker-compose.yml       # Postgres + Redis

frontend/
├── index.html               # Landing principal
├── carrito.html             # Carrito + checkout
├── pedido.html              # Tracking por código
├── admin/
│   ├── login.html           # Login admin
│   └── dashboard.html       # Panel administración
├── css/style.css            # Tema natural
└── js/                      # app.js, cart.js, admin.js
```

## API Endpoints

| Endpoint | Auth | Descripción |
|----------|------|-------------|
| `POST /auth/login` | — | Login admin → JWT |
| `GET /categorias` | — | Listar categorías |
| `POST /categorias` | Admin | Crear categoría |
| `GET /productos` | — | Listar productos |
| `POST /productos` | Admin | Crear producto |
| `PUT /productos/{id}` | Admin | Actualizar producto |
| `DELETE /productos/{id}` | Admin | Eliminar (soft) |
| `POST /productos/upload` | Admin | Subir imagen |
| `GET /productos/page?p=N` | — | HTML paginado (HTMX) |
| `GET /carrito` | Session | Ver carrito |
| `POST /carrito` | Session | Agregar item |
| `PUT /carrito/{id}` | Session | Actualizar cantidad |
| `DELETE /carrito/{id}` | Session | Eliminar item |
| `POST /pedidos` | Session | Crear pedido |
| `GET /pedidos` | Admin | Listar pedidos |
| `GET /pedidos/public/{id}` | — | Tracking público |
| `PUT /pedidos/{id}/estado` | Admin | Cambiar estado |
| `GET /envios/config` | Admin | Ver costos envío |
| `PUT /envios/config` | Admin | Actualizar costos |

## Tests

```bash
cd backend
uv run pytest -v    # 67 tests (SQLite, sin Docker)
```

## Admin por defecto

```
Email:    admin@nutristore.com
Password: admin123
```
