# Productos Specification

## Purpose

CRUD for products with image support (max 2), stock tracking by unit type (kg float / unidad int).

## Requirements

### Requirement: Create Product

The system MUST create products with a chosen unit type and validate stock type accordingly.

#### Scenario: Happy path

- GIVEN the requester has a valid admin JWT
- WHEN POST /productos with `{nombre, categoria_id, precio, tipo, stock, imagenes[]}`
- THEN the product is created
- AND stock is stored as FLOAT when tipo=kg, INTEGER when tipo=unidad

#### Scenario: Max images exceeded

- GIVEN the requester has a valid admin JWT
- WHEN POST /productos with 3 or more images
- THEN the response MUST be 422 with a validation error (max 2)

### Requirement: Stock Deduction

The system MUST deduct product stock when an order is placed.

#### Scenario: Kg deduction

- GIVEN a product with tipo=kg and stock=1.5
- WHEN an order includes that product with quantity=0.7
- THEN the product stock MUST be updated to 0.8

#### Scenario: Insufficient stock

- GIVEN a product with stock=0
- WHEN an order includes that product
- THEN order creation MUST fail with 409 Insufficient Stock
