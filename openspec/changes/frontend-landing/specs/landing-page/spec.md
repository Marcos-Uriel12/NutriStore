# Landing Page Specification

## Purpose

Public landing page (`index.html`) showcasing NutriStore with hero, about section, product grid with HTMX infinite scroll, and footer.

## Requirements

### Requirement: Navigation Bar

The page MUST display a sticky navbar with links to Inicio (`#`), Carrito (`/carrito.html`), and Mi Pedido (`/pedido.html`).

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| All links render | Page loads | User views navbar | Three links visible: Inicio, Carrito, Mi Pedido |
| Cart badge | Items exist in localStorage | Navbar renders | Badge with item count shown next to Carrito link |

### Requirement: Hero Section

The page MUST display a full-width hero section with a local exterior photo of the store.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Hero renders | Page loads | User views top of page | Hero with background image and store name/tagline is displayed |
| Responsive height | Viewport is mobile | User resizes browser | Hero height adjusts proportionally without cropping the image |

### Requirement: Quiénes Somos Section

The page MUST display a "Quiénes Somos" section with a local interior photo and descriptive text in a two-column layout.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Section renders | Page loads | User scrolls past hero | Two-column layout with photo and text is displayed |
| Mobile layout | Viewport is <768px | User views on phone | Columns stack vertically, photo above text |

### Requirement: Infinite Scroll Product Grid

The page MUST load products via HTMX infinite scroll, paginating through `GET /productos?page={n}`.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Initial load | Page loads | Product section enters viewport | HTMX fetches `GET /productos?page=1` and renders product cards |
| Scroll to next page | Products from page N are loaded | User scrolls to bottom of grid | HTMX fetches `GET /productos?page=N+1` and appends results |
| All products loaded | `page=N` returns empty array | User scrolls to bottom | No further requests are made; "No hay más productos" shown |
| Rapid scrolling | User scrolls quickly through pages | Multiple scroll events fire | Requests are debounced; only one page request is active at a time |

### Requirement: Footer

The page MUST display a footer with store contact information (address, phone, email).

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Footer renders | Page loads | User scrolls to bottom | Footer with address, phone, and email is displayed |

### Requirement: Theme Colors

The page MUST apply the theme palette: `#4a7c59` (verde), `#faf7f2` (blanco roto), `#d4c5a9` (beige).

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| CSS custom properties set | Page loads | User inspects `:root` styles | `--color-primary: #4a7c59`, `--color-bg: #faf7f2`, `--color-accent: #d4c5a9` are defined |
| Elements use theme | Any themed element renders | User inspects element | Backgrounds, buttons, and text use the theme palette consistently |
