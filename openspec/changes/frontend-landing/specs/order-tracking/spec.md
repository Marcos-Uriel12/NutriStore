# Order Tracking Specification

## Purpose

Order lookup page (`/pedido.html`) that displays order details by order code. No authentication required.

## Requirements

### Requirement: Order Code Input

The page MUST provide a text input and a "Consultar" button to search for an order by its code.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Input renders | Page loads | User views the page | Text input with placeholder "Ingresá tu código de pedido" and "Consultar" button are displayed |
| Pre-filled from URL | URL has `?codigo=ABC123` | Page loads | Input is pre-filled with "ABC123" and the lookup is triggered automatically |
| Empty input submitted | Input is empty | User clicks "Consultar" | Client-side validation prevents submission, "Ingresá un código válido" is shown |

### Requirement: Display Order Details

The page MUST fetch and display order details from `GET /pedidos/{codigo}`.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Order found | Order exists for the given code | User clicks "Consultar" | Order details are displayed: estado, items (name, qty, subtotal), total, tipo_entrega, fecha |
| Order not found | No order for the given code | User clicks "Consultar" | Message "Pedido no encontrado. Revisá el código e intentá de nuevo." is shown |
| API error | Backend is unavailable | User clicks "Consultar" | Error message "Error al consultar el pedido. Intentalo de nuevo." is shown |
| Different order queried | A previous result is displayed | User enters a new code and clicks "Consultar" | Previous result is replaced with the new order data |

### Requirement: Status Timeline

The page MUST display the order status as a visual timeline: pendiente → confirmado → entregado (or cancelado for terminal failure).

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Pending order | Order estado = pendiente | Details are displayed | Timeline shows "Pendiente" as active/current, remaining steps as pending |
| Delivered order | Order estado = entregado | Details are displayed | All steps (pendiente, confirmado, entregado) are marked complete |
| Cancelled order | Order estado = cancelado | Details are displayed | Timeline shows "Cancelado" as a terminal red state; remaining steps are grayed out |
| Confirmed order | Order estado = confirmado | Details are displayed | Timeline shows "Pendiente" and "Confirmado" as complete, "Entregado" as next step |
