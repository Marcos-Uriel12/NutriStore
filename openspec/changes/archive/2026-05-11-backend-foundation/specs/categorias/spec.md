# Categorias Specification

## Purpose

CRUD for product categories, enabling organization of products into logical groups.

## Requirements

### Requirement: Create Category

The system MUST allow admin users to create categories with a unique name.

#### Scenario: Happy path

- GIVEN the requester has a valid admin JWT
- WHEN POST /categorias with `{nombre, descripcion?}`
- THEN a new category is created
- AND its ID and name are returned

#### Scenario: Duplicate name

- GIVEN the requester has a valid admin JWT
- WHEN POST /categorias with a name that already exists
- THEN the response MUST be 409 Conflict

### Requirement: List Categories

The system MUST return all categories for any request (no auth required).

#### Scenario: Categories exist

- GIVEN categories exist in the database
- WHEN GET /categorias
- THEN the response MUST return an array of categories

#### Scenario: No categories

- GIVEN no categories exist
- WHEN GET /categorias
- THEN the response MUST return an empty array
