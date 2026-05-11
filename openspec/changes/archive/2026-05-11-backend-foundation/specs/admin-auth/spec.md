# Admin Auth Specification

## Purpose

JWT-based authentication for admin users plus an initial admin seeder on first startup.

## Requirements

### Requirement: Admin Login

The system MUST accept email+password and return a signed JWT on valid credentials.

#### Scenario: Successful login

- GIVEN an admin account exists in the database
- WHEN POST /auth/login with valid email and password
- THEN the response MUST contain a `token` field with a signed JWT
- AND the JWT MUST expire after a configurable TTL

#### Scenario: Invalid credentials

- GIVEN an admin account exists
- WHEN POST /auth/login with incorrect password
- THEN the response MUST be 401 Unauthorized

### Requirement: Admin Seeder

The system MUST seed an initial admin account on first startup.

#### Scenario: First startup

- GIVEN no admin accounts exist in the database
- WHEN the application starts
- THEN a default admin is created with credentials from environment variables

#### Scenario: Already seeded

- GIVEN an admin account already exists
- WHEN the application starts
- THEN the seeder MUST NOT create a duplicate account
