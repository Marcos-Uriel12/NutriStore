# Admin Dashboard Specification

## Purpose

Protected admin dashboard (`/admin/dashboard.html`) with tabbed CRUD interfaces for Productos, Categorías, and Pedidos. All API calls include the JWT from localStorage.

## Requirements

### Requirement: Auth Guard

The page MUST redirect to `/admin/login.html` if no valid `jwt_token` is found in localStorage.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Authenticated | `jwt_token` exists and is valid | Page loads | Dashboard renders with tab navigation |
| Unauthenticated | No `jwt_token` in localStorage | Page loads | Redirect to `/admin/login.html` |
| Expired token | `jwt_token` exists but is expired | Any API call returns 401 | Token cleared from localStorage, redirect to `/admin/login.html` |

### Requirement: Tab Navigation

The page MUST display three tabs: Productos, Categorías, Pedidos. Only one tab's content is visible at a time.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Default tab | Page loads | User views dashboard | Productos tab is active by default; others are hidden |
| Switch tabs | Any tab is active | User clicks a different tab | Active tab content hides, selected tab content shows, URL hash updates |

### Requirement: Productos CRUD

The Productos tab MUST display a table of products with columns: nombre, precio, categoria, activo. CRUD operations use `GET/POST/PUT/DELETE /productos` with JWT.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| List products | Products exist in database | Productos tab loads | Table renders with all products (excluding soft-deleted ones) |
| Create product | User is on Productos tab | User clicks "Agregar" and fills modal form | `POST /productos` is called with form data, new product appears in table, success toast shown |
| Edit product | A product row is visible | User clicks "Editar" and modifies fields inline | `PUT /productos/{id}` is called, row updates without page reload |
| Soft delete product | A product row is visible | User clicks "Eliminar" and confirms | `DELETE /productos/{id}` is called, row is hidden from table (soft delete) |
| Create validation fails | Required fields are empty | User submits create modal form | Form is not submitted, field validation errors shown in modal |
| API error on edit | Backend returns error | User tries to save an edit | Error message displayed, row reverts to previous values |

### Requirement: Categorías CRUD

The Categorías tab MUST display a table of categories with name and description. CRUD via `GET/POST/PUT/DELETE /categorias` with JWT.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| List categories | Categories exist | Categorías tab loads | Table renders with all categories |
| Create category | User is on Categorías tab | User clicks "Agregar categoría" | Modal with name+description fields shown, `POST /categorias` on submit, table updates |
| Edit category | A category row is visible | User clicks "Editar" | Inline editing activated, `PUT /categorias/{id}` on save, row updates |
| Delete category | A category row exists | User clicks "Eliminar" | `DELETE /categorias/{id}` called, row removed, success feedback |
| Delete protected category | Category has associated products | User tries to delete | Backend returns error, message "No se puede eliminar una categoría con productos" shown |

### Requirement: Pedidos Management

The Pedidos tab MUST display a table of orders with columns: código, cliente, total, estado, fecha. Estado can be updated via dropdown.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| List orders | Orders exist | Pedidos tab loads | Table with all orders, latest first, is displayed |
| Update estado | An order row is displayed | User selects new estado from dropdown | `PUT /pedidos/{codigo}/estado` is called with JWT, estado cell updates, success feedback |
| Invalid transition | Current estado is "entregado" | User tries to change from "entregado" to another state | Backend rejects, error message shown, dropdown reverts |
| Filter by estado | Multiple orders with different estados | User selects a filter option | Table filters to show only matching orders |
