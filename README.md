# 🌿 NutriStore

Sistema de gestión integral para dietética — backend API + frontend web.

🔗 **Demo en vivo:** [nutristore-backend.onrender.com](https://nutristore-backend.onrender.com)
🔗 **Panel admin:** [nutristore-backend.onrender.com/admin/login.html](https://nutristore-backend.onrender.com/admin/login.html)

---

## 📸 Capturas

| Landing | Admin Dashboard | Carrito |
|---------|----------------|---------|
| Productos con scroll infinito + quiénes somos | CRUD productos, categorías, pedidos, envíos | Carrito anónimo con checkout |

---

## 🚀 Demo rápida

| | |
|---|---|
| **Landing pública** | [https://nutristore-backend.onrender.com](https://nutristore-backend.onrender.com) |
| **Admin** | [https://nutristore-backend.onrender.com/admin/login.html](https://nutristore-backend.onrender.com/admin/login.html) |
| **Email admin** | `admin@nutristore.com` |
| **Password** | `admin123` |

> ⚡ Tips para probar:
> 1. Andá a la landing → scrolleá para ver productos con scroll infinito
> 2. Agregá productos al carrito
> 3. Andá a `/carrito.html` → completá el checkout
> 4. Seguí tu pedido en `/pedido.html` con el código
> 5. Admin: gestioná productos, cambiá estados de pedidos, configurá envíos

---

## 🧱 Stack

### Backend
| Tecnología | Uso |
|-----------|-----|
| **Python 3.12** + **FastAPI** | API REST async |
| **SQLAlchemy 2.0** (async) | ORM |
| **PostgreSQL 16** | Base de datos |
| **Redis 7** | Carrito anónimo (session) |
| **Alembic** | Migraciones |
| **JWT** (python-jose) | Autenticación admin |
| **Pydantic v2** | Schemas y validación |
| **passlib** + **bcrypt** | Hashing de contraseñas |

### Frontend
| Tecnología | Uso |
|-----------|-----|
| **Bootstrap 5** | Layout y componentes |
| **HTMX 2** | Scroll infinito, carga dinámica |
| **CSS custom** | Tema natural verde/beige/blanco |
| **Vanilla JS** | Carrito, admin, session management |

### DevOps
| Herramienta | Uso |
|------------|-----|
| **Docker Compose** | PostgreSQL + Redis local |
| **uv** | Gestor de paquetes Python |
| **pytest** + httpx + fakeredis | Tests (67 tests, SQLite) |
| **Render** | Deploy producción |

---

## 📁 Estructura del proyecto

```
nutristore/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + routers + static files
│   │   ├── config.py            # Pydantic Settings (env vars)
│   │   ├── database.py          # Async SQLAlchemy engine + session
│   │   ├── dependencies.py      # JWT guard + Redis dependency
│   │   ├── email_service.py     # Notificaciones por email (SMTP)
│   │   ├── models/              # 8 modelos SQLAlchemy
│   │   │   ├── admin.py         # Admin (JWT auth)
│   │   │   ├── categoria.py     # Categorías de productos
│   │   │   ├── producto.py      # Productos + TipoUnidad enum
│   │   │   ├── imagen.py        # Imágenes (max 2 por producto)
│   │   │   ├── pedido.py        # Pedidos + EstadoPedido enum
│   │   │   ├── pedido_item.py   # Items del pedido
│   │   │   ├── pago.py          # Pagos (efectivo/transferencia)
│   │   │   └── envio.py         # Config zonas de envío
│   │   ├── usuarios/            # Auth: login + register
│   │   ├── productos/           # CRUD productos + categorías
│   │   ├── carrito/             # Carrito Redis por session_id
│   │   ├── pedidos/             # Pedidos + state machine
│   │   └── envios/              # Config zonas y costos
│   ├── alembic/                 # Migraciones automáticas
│   ├── tests/                   # 67 tests (pytest)
│   │   ├── test_models.py       # Tests de modelos
│   │   ├── test_alembic.py      # Test de migración
│   │   ├── test_auth.py         # Tests de autenticación
│   │   ├── test_productos.py    # Tests CRUD productos
│   │   ├── test_carrito.py      # Tests carrito (fakeredis)
│   │   ├── test_pedidos.py      # Tests pedidos + estados
│   │   └── test_envios.py       # Tests configuración envíos
│   ├── scripts/
│   │   ├── seed.py              # Seed del admin inicial
│   │   └── seed_productos.py    # Seed de productos de prueba
│   ├── docker-compose.yml       # PostgreSQL 16 + Redis 7
│   ├── Dockerfile               # Python 3.12 slim + uv
│   └── pyproject.toml           # Dependencias y config
│
├── frontend/
│   ├── index.html               # Landing: hero + quiénes somos + productos
│   ├── carrito.html             # Carrito + formulario de checkout
│   ├── pedido.html              # Tracking de pedido por código
│   ├── admin/
│   │   ├── login.html           # Login admin
│   │   └── dashboard.html       # Panel: tabs productos/categorías/pedidos/envíos
│   ├── css/
│   │   └── style.css            # Tema natural (verde #4a7c59, beige #d4c5a9)
│   └── js/
│       ├── config.js            # Config API_BASE para deploy
│       ├── app.js               # Session ID + cart badge
│       ├── cart.js              # API cliente del carrito
│       └── admin.js             # JWT guard + admin API wrapper
│
├── openspec/                    # SDD artifacts (especificaciones)
└── README.md
```

---

## 🚀 Inicio rápido (local)

```bash
# 1. Clonar
git clone https://github.com/Marcos-Uriel12/NutriStore.git
cd NutriStore/backend

# 2. Configurar entorno
cp .env.example .env             # Editar credenciales
uv sync                          # Instalar dependencias

# 3. Levantar base de datos y Redis
docker compose up -d

# 4. Migraciones
uv run alembic upgrade head

# 5. Cargar datos de prueba (opcional)
uv run python -m scripts.seed_productos

# 6. Iniciar servidor
uv run uvicorn app.main:app --reload --host 0.0.0.0

# 7. Abrir en el navegador
open http://localhost:8000
```

---

## 📋 API Endpoints

### Auth
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `POST` | `/auth/login` | — | Login admin → JWT token |
| `GET` | `/auth/me` | Admin | Datos del admin autenticado |

### Categorías
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/categorias` | — | Listar todas las categorías |
| `POST` | `/categorias` | Admin | Crear nueva categoría |

### Productos
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/productos` | — | Listar productos activos |
| `GET` | `/productos/{id}` | — | Detalle del producto |
| `GET` | `/productos/page` | — | HTML paginado (HTMX) |
| `POST` | `/productos` | Admin | Crear producto |
| `PUT` | `/productos/{id}` | Admin | Actualizar producto |
| `DELETE` | `/productos/{id}` | Admin | Soft delete (activo=false) |
| `POST` | `/productos/upload` | Admin | Subir imagen |

### Carrito (anónimo por session_id)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/carrito` | Session | Ver items del carrito |
| `POST` | `/carrito` | Session | Agregar item |
| `PUT` | `/carrito/{id}` | Session | Actualizar cantidad |
| `DELETE` | `/carrito/{id}` | Session | Eliminar item |
| `DELETE` | `/carrito` | Session | Vaciar carrito |

### Pedidos
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `POST` | `/pedidos` | Session | Crear pedido desde carrito |
| `GET` | `/pedidos` | Admin | Listar todos los pedidos |
| `GET` | `/pedidos/public/{id}` | — | Tracking público por ID |
| `PUT` | `/pedidos/{id}/estado` | Admin | Cambiar estado |

### Envíos
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/envios/config` | Admin | Ver zonas y costos |
| `PUT` | `/envios/config` | Admin | Actualizar configuración |

---

## 🧪 Tests

```bash
cd backend

# Todos los tests (67, sin Docker — usa SQLite)
uv run pytest -v

# Por dominio
uv run pytest tests/test_models.py -v
uv run pytest tests/test_auth.py -v
uv run pytest tests/test_productos.py -v
uv run pytest tests/test_carrito.py -v
uv run pytest tests/test_pedidos.py -v
uv run pytest tests/test_envios.py -v
```

---

## 🌱 Seed de datos de prueba

```bash
cd backend

# Admin por defecto (se crea automáticamente al iniciar)
# Email: admin@nutristore.com / Password: admin123

# Productos de prueba (10 productos en 4 categorías)
uv run python -m scripts.seed_productos
```

---

## 🎨 Tema visual

| Color | Hex | Uso |
|-------|-----|-----|
| Verde principal | `#4a7c59` | Botones, navbar, títulos |
| Verde oscuro | `#3d6349` | Footer, hover states |
| Fondo | `#faf7f2` | Background general |
| Beige/madera | `#d4c5a9` | Acentos, bordes, cards |
| Texto | `#2c3e2d` | Textos principales |

---

## 📧 Email automáticos

Al crear un pedido se envían automáticamente:

- 📬 **Confirmación al cliente** con detalle de productos y total
- 🔔 **Notificación al admin** con datos del cliente y pedido

Configurar en `backend/.env`:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
```

---

## 🔗 Enlaces

| Recurso | URL |
|---------|-----|
| **Producción** | [https://nutristore-backend.onrender.com](https://nutristore-backend.onrender.com) |
| **Admin** | [https://nutristore-backend.onrender.com/admin/login.html](https://nutristore-backend.onrender.com/admin/login.html) |
| **Repositorio** | [github.com/Marcos-Uriel12/NutriStore](https://github.com/Marcos-Uriel12/NutriStore) |
| **Documentación API** | [https://nutristore-backend.onrender.com/docs](https://nutristore-backend.onrender.com/docs) |

---

> 🛠️ Desarrollado con SDD (Spec-Driven Development) — [Marcos-Uriel12](https://github.com/Marcos-Uriel12)
