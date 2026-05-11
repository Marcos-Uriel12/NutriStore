# Pagos Specification

## Purpose

Payment method tracking for orders. No payment gateway integration — only registro of efectivo or transferencia.

## Requirements

### Requirement: Register Payment Method

The system MUST record the payment method when an order is created.

#### Scenario: Valid method

- GIVEN an order creation request
- WHEN the request includes metodo_pago=efectivo or transferencia
- THEN a payment record is created linked to the order

#### Scenario: Invalid method

- GIVEN an order creation request
- WHEN the request includes an unsupported metodo_pago
- THEN the response MUST be 422 Validation Error

### Requirement: Payment Query

The system MUST allow admin to view payment info for any order.

#### Scenario: Payment exists

- GIVEN an order with a payment record
- WHEN GET /pedidos/{id} (admin)
- THEN the response MUST include the payment method and status

#### Scenario: No payment

- GIVEN an order with no payment record
- WHEN GET /pedidos/{id}
- THEN the response MUST return payment as null
