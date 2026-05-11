# Tasks: Frontend Landing y Páginas Públicas

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1500-2000 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR #1 (backend) → PR #2 (frontend) |
| Delivery strategy | ask-on-risk |
| Chain strategy | feature-branch-chain |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Backend mods: mount, pagination, cart ops, enriched response, pedido lookup | PR 1 | No frontend deps |
| 2 | Frontend: CSS/JS infra + all 5 pages | PR 2 | Depends on PR 1 endpoints |

## Phase 1: Backend Modifications

- [x] 1.1 `app/main.py` — Mount frontend/ as StaticFiles with catch-all fallback
- [x] 1.2 `productos/router.py` — GET /productos/page returning Bootstrap cards
- [x] 1.3 `carrito/router.py` — PUT/DELETE by producto_id
- [x] 1.4 `carrito/schemas.py` — Enrich CartItemResponse (nombre, precio, imagen)
- [x] 1.5 `pedidos/router.py` — GET /pedidos/public/{pedido_id} (no auth)

## Phase 2: CSS + JS Infrastructure

- [x] 2.1 `css/style.css` — Theme: custom properties, button/card/navbar/footer/hero
- [x] 2.2 `js/app.js` — Session ID UUID, X-Session-ID header, HTMX config
- [x] 2.3 `js/cart.js` — Cart fetch API: add/update/remove/get/checkout
- [x] 2.4 `js/admin.js` — JWT localStorage, auth header, login/logout/guard

## Phase 3: Frontend Pages

- [x] 3.1 `index.html` — Navbar, hero, quiénes somos 2-col, product infinite scroll, footer
- [x] 3.2 `carrito.html` — Cart table, modify/remove, checkout form with conditional fields
- [x] 3.3 `pedido.html` — Code input, pre-fill from URL, order details + timeline
- [x] 3.4 `admin/login.html` — Login form, POST /auth/login, store JWT, redirect
- [x] 3.5 `admin/dashboard.html` — Auth guard, tabs (productos/categorías/pedidos), CRUD modals

## Phase 4: Verification

- [ ] 4.1 All pages serve correctly from FastAPI static mount
- [ ] 4.2 HTMX product infinite scroll (no dupes, "no más" terminal)
- [ ] 4.3 Cart flow: add/update/remove/checkout via session_id
- [ ] 4.4 Admin login + JWT + CRUD tabs
- [ ] 4.5 Order lookup by code + status timeline rendering
