# Carrito Specification

## Purpose

Anonymous cart stored in Redis, keyed by session_id. No user authentication required.

## Requirements

### Requirement: Add to Cart

The system MUST add items to a cart identified by session_id.

#### Scenario: New item

- GIVEN a valid session_id
- WHEN POST /carrito with `{producto_id, cantidad}`
- THEN the item is stored in Redis under that session_id

#### Scenario: Duplicate item

- GIVEN a session_id with an existing producto_id
- WHEN POST /carrito with the same producto_id
- THEN the existing quantity is updated (not duplicated)

### Requirement: Clear Cart on Order

The system MUST delete the cart after a successful order.

#### Scenario: Order placed

- GIVEN a session_id with items in Redis
- WHEN POST /pedidos succeeds for that session_id
- THEN the Redis key for that session_id is deleted

#### Scenario: Empty cart inquiry

- GIVEN a session_id with no items
- WHEN GET /carrito
- THEN the response MUST return an empty items array
