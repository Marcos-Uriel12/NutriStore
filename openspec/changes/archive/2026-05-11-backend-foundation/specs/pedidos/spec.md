# Pedidos Specification

## Purpose

Order creation from cart, state machine, delivery type support, and querying.

## Requirements

### Requirement: Create Order

The system MUST create an order from the current cart, capturing customer data on the fly.

#### Scenario: Happy path

- GIVEN a session_id has items in Redis
- WHEN POST /pedidos with `{nombre, direccion, telefono, tipo_entrega, metodo_pago, zona_envio?}`
- THEN an order is created with estado=pendiente
- AND all cart items become order items
- AND the Redis cart is cleared

#### Scenario: Empty cart

- GIVEN a session_id with an empty cart
- WHEN POST /pedidos
- THEN the response MUST be 400 Bad Request (empty cart)

### Requirement: Order State Machine

The system MUST transition orders through estados: pendiente → confirmado → entregado | cancelado.

#### Scenario: Confirm order

- GIVEN an order with estado=pendiente
- WHEN PUT /pedidos/{id}/estado with `{estado: confirmado}`
- THEN the order estado changes to confirmado

#### Scenario: Cannot cancel delivered

- GIVEN an order with estado=entregado
- WHEN PUT /pedidos/{id}/estado with `{estado: cancelado}`
- THEN the response MUST be 400 Bad Request

### Requirement: Delivery Type

The system MUST support envío and retiro delivery types.

#### Scenario: Envío with cost

- GIVEN an order with tipo_entrega=envío
- WHEN the order is created
- THEN it MUST include zona_envio and costo_envio based on envios-config

#### Scenario: Retiro sin costo

- GIVEN an order with tipo_entrega=retiro
- WHEN the order is created
- THEN costo_envio MUST be 0
- AND zona_envio MUST be null
