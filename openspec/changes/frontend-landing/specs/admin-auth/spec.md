# Delta for Admin Auth

## ADDED Requirements

### Requirement: Frontend Login Page

The system MUST provide an HTML login page at `/admin/login.html` with an email+password form that calls `POST /auth/login` and stores the returned JWT in `localStorage`.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Successful login | Valid admin account exists | User submits valid email + password | `POST /auth/login` returns JWT, stored as `jwt_token` in localStorage, redirect to `/admin/dashboard.html` |
| Invalid credentials | Valid admin account exists | User submits wrong password | 401 response is caught, error message "Credenciales inválidas" shown on page, no redirect, localStorage unchanged |
| Empty email field | Login form is displayed | User submits with empty email | Client-side validation prevents submission, "El email es requerido" shown |
| Empty password field | Login form is displayed | User submits with empty password | Client-side validation prevents submission, "La contraseña es requerida" shown |

### Requirement: JWT Expiry Guard

Admin pages MUST intercept 401 responses from API calls and redirect to `/admin/login.html`, clearing the expired token.

| Scenario | GIVEN | WHEN | THEN |
|----------|-------|------|------|
| Expired token on API call | `jwt_token` exists but is expired | Admin page makes an authenticated API call | API returns 401, token is removed from localStorage, redirect to `/admin/login.html` |
| Missing token on page load | No `jwt_token` in localStorage | User navigates to `/admin/dashboard.html` | JavaScript redirects to `/admin/login.html` immediately |
| Valid token | `jwt_token` is valid and not expired | Admin page loads or makes API call | No redirect occurs, page renders normally |

## Existing Backend Spec

The existing `openspec/specs/admin-auth/spec.md` requirements (Admin Login, Admin Seeder) remain unchanged — they describe the backend API behavior. No modifications to backend requirements.
