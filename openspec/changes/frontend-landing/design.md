# Design: Frontend Landing y Páginas Públicas

## Technical Approach

FastAPI sirve `frontend/` como static files. Bootstrap 5 + HTMX (CDN) para layout y carga dinámica, vanilla JS para carrito y admin. Sin SPA framework — HTML planos con progressive enhancement via HTMX. Las imágenes locales (`local_exterior.png`, `local_interior.png`) ya existen en `frontend/img/`.

Se requieren cambios mínimos al backend para habilitar paginación de productos y endpoints faltantes de carrito/pedidos.

## Architecture Decisions

| Decisión | Opciones | Tradeoffs | Decisión |
|----------|----------|-----------|----------|
| **Serving frontend** | (A) FastAPI StaticFiles + catch-all, (B) Nginx aparte | (A) un solo `uv run uvicorn`, sin infra extra; (B) más overhead | **A** — StaticFiles montado en `main.py` con catch-all para HTML directo |
| **Productos paginados** | (A) Modificar GET /productos con ?page&limit, (B) Endpoint HTML separado | (A) rompe contrato existente; (B) limpio, mantiene JSON API intacta | **B** — Nueva ruta `GET /productos/page?p=N&limit=8` que devuelve HTML fragments para HTMX |
| **Cart item ops individuales** | (A) PUT/DELETE por producto_id en carrito, (B) Reemplazar carrito entero | (A) semántica REST correcta; (B) race conditions | **A** — `PUT /carrito/{producto_id}` (update cantidad), `DELETE /carrito/{producto_id}` (remove item) |
| **Order tracking lookup** | (A) Exponer GET /pedidos/{id} público, (B) Código alfanumérico separado | (A) usa id existente, sin migración; (B) requiere migration + columna `codigo` | **A** — Endpoint público `GET /pedidos/public/{pedido_id}` (sin auth). El "código" es el pedido_id |
| **Cart response con nombres** | (A) Incluir datos del producto en CartItemResponse, (B) Fetch separado desde JS | (A) backend join, data correcta; (B) N+1 requests, lenta | **A** — Modificar CartItemResponse para incluir nombre y precio del producto |
| **Session ID** | localStorage vs cookie | cookie vulnerable a CSRF; localStorage controlable desde JS | **localStorage** como `nutristore_session_id`, enviado vía `X-Session-ID` header |
| **JWT admin** | localStorage vs httpOnly cookie | httpOnly más seguro pero requiere backend para login flow; localStorage simple | **localStorage** como `nutristore_token`, enviado vía `Authorization: Bearer`. Guard en `admin.js` |
| **Infinite scroll** | HTMX `hx-trigger="revealed"` vs IntersectionObserver JS | HTMX nativo, sin JS extra; debounce necesario para evitar múltiples requests | **HTMX reveal** con sentinel `<div hx-trigger="revealed">` al final del grid |

## Data Flow

```
index.html (landing)
  ├─ Navbar sticky [Bootstrap]
  ├─ Hero full-width con img/local_exterior.png [CSS fondo]
  ├─ Quiénes Somos 2-columnas con img/local_interior.png
  ├─ Productos grid
  │    └─ div#product-list
  │         └─ hx-get="/productos/page?p=1" hx-trigger="load"
  │              └─ Cada card: "Agregar" → POST /carrito (fetch con session_id)
  │                   └─ Sentinel: hx-get="?p=N+1" hx-trigger="revealed"
  │                        └─ Last page: "No hay más productos" detiene trigger
  └─ Footer contacto

carrito.html
  ├─ GET /carrito via fetch(X-Session-ID) → tabla items
  ├─ +/- calls PUT /carrito/{producto_id}
  ├─ Eliminar calls DELETE /carrito/{producto_id}
  └─ Checkout POST /pedidos → redirect /pedido.html?codigo={id}

pedido.html
  └─ GET /pedidos/public/{id} (público) → detalles + timeline visual
       └─ Estados: pendiente → confirmado → entregado (o cancelado rojo)

admin/login.html
  └─ POST /auth/login → almacena jwt_token → redirect a /admin/dashboard.html

admin/dashboard.html
  └─ hx-get tabs: /admin/productos-table | /admin/categorias-table | /admin/pedidos-table
       └─ Modales Bootstrap para CRUD forms
```

## Backend Modifications

| Endpoint | Archivo | Cambio |
|----------|---------|--------|
| `GET /productos/page?p=N&limit=8` | `productos/router.py` | **Nuevo** — HTML fragment con cards, offset=(p-1)*limit |
| `PUT /carrito/{producto_id}` | `carrito/router.py` | **Nuevo** — update cantidad, body: `{"cantidad": N}` |
| `DELETE /carrito/{producto_id}` | `carrito/router.py` | **Nuevo** — remove single item from Redis hash |
| `GET /pedidos/public/{pedido_id}` | `pedidos/router.py` | **Nuevo** — público (sin auth), lookup por id |
| CartItemResponse | `carrito/schemas.py` | **Modificar** — agregar `nombre`, `precio` del producto |
| Static mount | `main.py` | **Modificar** — `app.mount("/", StaticFiles(directory="frontend", html=True))` |

## File Changes

| File | Acción | Descripción |
|------|--------|-------------|
| `frontend/index.html` | Create | Landing: hero, quienes-somos, productos HTMX, footer |
| `frontend/carrito.html` | Create | Tabla carrito + checkout form |
| `frontend/pedido.html` | Create | Búsqueda de pedido + timeline |
| `frontend/admin/login.html` | Create | Login form (email + password) |
| `frontend/admin/dashboard.html` | Create | Tabs (productos, categorías, pedidos) con modales |
| `frontend/css/style.css` | Create | Tema: `--color-primary: #4a7c59`, `--color-bg: #faf7f2`, `--color-accent: #d4c5a9` |
| `frontend/js/app.js` | Create | Session ID init, HTMX config headers, helpers |
| `frontend/js/cart.js` | Create | Cart CRUD via fetch + localStorage sync |
| `frontend/js/admin.js` | Create | JWT storage, auth guard, fetch wrapper con 401 redirect |
| `backend/app/main.py` | Modify | StaticFiles mount + catch-all |
| `backend/app/productos/router.py` | Modify | Add paginated HTML fragment endpoint |
| `backend/app/carrito/router.py` | Modify | Add PUT/DELETE by producto_id |
| `backend/app/pedidos/router.py` | Modify | Add public GET by id |
| `backend/app/carrito/schemas.py` | Modify | Add producto nombre + precio to response |

## Testing Strategy

| Capa | Qué probar | Cómo |
|------|------------|------|
| Visual | 5 páginas renderizan correctamente con tema | Inspección manual en navegador |
| HTMX | Scroll infinito carga productos sin duplicados | Verificar red en DevTools, última página muestra "No hay más" |
| Cart | Add/update/remove items + checkout | localStorage + DevTools Network |
| Admin | Login JWT, CRUD productos/categorías, cambio estado pedido | Flujo completo manual |
| Error states | 401 redirect, carrito vacío, pedido no encontrado | Casos borde manuales |

## Open Questions

None — todas las decisiones están resueltas en la tabla de Architecture Decisions.
