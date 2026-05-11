# Proposal: Frontend Landing y Páginas Públicas

## Intent

Crear el frontend público de NutriStore: landing, carrito anónimo, consulta de pedidos y panel admin. Los endpoints backend ya existen; esta propuesta cubre solo la capa de presentación con Bootstrap 5 + HTMX + tema natural/verde.

## Scope

| In Scope | Out of Scope |
|----------|-------------|
| Landing: hero, quiénes somos, scroll infinito (HTMX), footer | Pasarela de pagos |
| Carrito con session_id en localStorage + Redis | Registro de usuarios |
| Consulta de pedido por código de compra | SEO / SSR |
| Admin login JWT + dashboard con tabs (Productos CRUD, Categorías CRUD, Pedidos) | Tests automatizados del frontend |
| Tema visual: verde #4a7c59, blanco roto #faf7f2, beige #d4c5a9 | |

## Capabilities

### New Capabilities
- `landing-page`: Hero + Quiénes Somos + Productos scroll infinito + Footer
- `cart-page`: Ver y modificar carrito desde el frontend
- `order-tracking`: Consultar pedido por código de compra
- `admin-dashboard`: CRUD productos, categorías y gestión de pedidos

### Modified Capabilities
- `admin-auth`: Se agrega login page HTML + flujo JWT desde frontend

## Approach

SPA-like con HTML planos. Bootstrap 5 CDN para layout, HTMX para carga dinámica de productos con scroll infinito, CSS custom para tema natural. Vanilla JS para carrito (localStorage + fetch a API) y admin dashboard. Sin framework JS pesado. Session_id UUID generado en localStorage al primer ingreso.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `frontend/index.html` | New | Landing page principal |
| `frontend/carrito.html` | New | Vista del carrito |
| `frontend/pedido.html` | New | Consulta de pedido |
| `frontend/admin/login.html` | New | Login admin |
| `frontend/admin/dashboard.html` | New | Panel admin con tabs |
| `frontend/css/theme.css` | New | Tema natural/verde |
| `frontend/js/cart.js` | New | Lógica de carrito + localStorage |
| `frontend/js/admin.js` | New | Lógica de admin dashboard |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| HTMX scroll infinito sin rate-limit | Low | Debounce en trigger htmx:load |
| session_id perdido en localStorage | Low | Regenerar UUID si no existe |

## Rollback Plan

Revertir los archivos HTML/JS/CSS nuevos. Sin cambios en backend, rollback trivial (borrar archivos agregados).

## Dependencies

- Backend APIs de productos, carrito, pedidos, admin-auth ya implementadas
- Bootstrap 5 vía CDN
- HTMX vía CDN

## Success Criteria

- [ ] Landing carga hero, quiénes somos con fotos locales, productos con scroll infinito
- [ ] Carrito persiste en localStorage y se sincroniza con backend Redis
- [ ] Pedido consultable por código sin login
- [ ] Admin login con JWT redirige a dashboard con tabs funcionales
