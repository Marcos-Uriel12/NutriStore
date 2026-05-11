# Cart Page Specification

## Purpose

Cart view page (`/carrito.html`) that displays items from the backend cart API using `session_id` from localStorage, and provides a checkout form that submits to `POST /pedidos`.

## Requirements

### Requirement: View Cart Items

The page MUST fetch cart items from `GET /carrito` using the `session_id` stored in localStorage.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Cart has items | `session_id` exists with items in Redis | Page loads | Items with name, quantity, unit price, and subtotal are rendered in a table |
| Cart is empty | `session_id` exists with no items | Page loads | A message "Tu carrito está vacío" is shown with a link to the landing page |
| No session_id | No `session_id` in localStorage | Page loads | A new UUID is generated, stored in localStorage, and empty cart is displayed |

### Requirement: Modify Quantities

The page MUST allow the user to increase or decrease item quantities and reflect changes via `PUT /carrito/{producto_id}`.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Increase quantity | Item is in cart | User clicks "+" | Quantity increases by 1, `PUT /carrito/{id}` is called, subtotal updates |
| Decrease quantity | Item has quantity > 1 | User clicks "−" | Quantity decreases by 1, `PUT /carrito/{id}` is called, subtotal updates |
| Decrease to zero | Item has quantity = 1 | User clicks "−" | Item is removed from cart via `DELETE /carrito/{id}`, row disappears |
| Quantity update fails | Backend is unavailable | User clicks "+" or "−" | Error message is shown, quantity reverts to previous value |

### Requirement: Remove Items

The page MUST allow removing an item entirely via `DELETE /carrito/{producto_id}`.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Remove item | Item is in cart | User clicks "Eliminar" | Item is removed, cart total recalculates, confirmation feedback shown |
| Remove fails | Backend returns error | User clicks "Eliminar" | Error message displayed, item remains in cart |

### Requirement: Checkout Form

The page MUST display a checkout form requiring: nombre, dirección, teléfono, tipo_entrega (envío/retiro), zona_envío (if envío), and metodo_pago.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Form renders | Cart has items | User scrolls to checkout section | Form fields are displayed: nombre, dirección, teléfono, tipo_entrega (radio), zona_envío (conditional), metodo_pago (select) |
| Delivery address required | tipo_entrega = envío | User selects "Envío" | zona_envío field appears and is required |
| Pickup hides address | tipo_entrega = retiro | User selects "Retiro" | zona_envío field is hidden and not required |

### Requirement: Submit Order

The page MUST POST to `/pedidos` on form submit and redirect to a confirmation page with the order code.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Order submitted successfully | Cart has items and form is valid | User clicks "Confirmar Pedido" | `POST /pedidos` is called with session_id and form data, on success redirects to `/pedido.html?codigo={codigo}` |
| Order fails | Backend returns error | User submits form | Error message is shown, form data is preserved, cart is not cleared |
| Empty cart submitted | Cart has no items | User submits form | Submission is blocked client-side, message "Agregá productos al carrito" is shown |
| Missing required fields | One or more fields are empty | User submits form | Client-side validation highlights the missing fields, submission prevented |
