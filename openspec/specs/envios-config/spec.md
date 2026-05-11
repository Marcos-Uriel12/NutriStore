# Envios Config Specification

## Purpose

Configurable shipping zones and costs, managed by admin users only.

## Requirements

### Requirement: Read Config

The system MUST return the current shipping configuration.

#### Scenario: Config exists

- GIVEN shipping config has been set
- WHEN GET /envios/config (admin)
- THEN the response MUST return zonas with their costos

#### Scenario: Default config

- GIVEN no shipping config has been set yet
- WHEN GET /envios/config (admin)
- THEN the response MUST return default zones (CABA: 3500, GBA_NORTE: 3500)

### Requirement: Update Config

The system MUST allow admin users to update shipping zones and costs.

#### Scenario: Happy path

- GIVEN the requester has a valid admin JWT
- WHEN PUT /envios/config with `{zonas: [{nombre, costo}]}`
- THEN the config is updated
- AND subsequent reads return the new values

#### Scenario: Unauthorized

- GIVEN the requester has NO valid JWT
- WHEN PUT /envios/config
- THEN the response MUST be 401 Unauthorized
