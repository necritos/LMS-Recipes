# Documentación API — Recetario v1

Backend REST JSON para plataforma LMS + E-commerce. **Solo APIs** — el frontend es un proyecto separado.

## Base URL

```
http://localhost:8000/api/v1/     # desarrollo
https://api.tudominio.com/api/v1/ # producción
```

## Superficies

| Carpeta | Audiencia | Prefijo URL | Auth |
|---------|-----------|-------------|------|
| [auth/](./auth/) | Usuario final | `/api/v1/auth/` | JWT `type=user` |
| [admin/](./admin/) | Staff / administración | `/api/v1/admin/` | JWT `type=staff` |
| public/ *(fase 2+)* | Visitantes | `/api/v1/public/` | Ninguna |

## Convenciones globales

| Tema | Detalle |
|------|---------|
| Éxito (recurso) | `{ "data": { ... }, "meta": {} }` |
| Error | `{ "error": { "code", "message", "details" } }` |
| Listas paginadas | `{ "count", "next", "previous", "results" }` |
| Auth header | `Authorization: Bearer <access_token>` |
| OpenAPI / Swagger | `/api/docs/` y `/api/schema/` |

## JWT — tipos de token

| type | Actor | Modelo | Login |
|------|-------|--------|-------|
| `user` | Cliente / estudiante | `UserAccount` | `POST /auth/login/` |
| `staff` | Administrador | `StaffUser` | `POST /admin/auth/login/` |

## Índice de endpoints — Auth (Fase 1)

| Método | Ruta | Documento |
|--------|------|-----------|
| POST | `/auth/register/` | [register.md](./auth/register.md) |
| POST | `/auth/login/` | [login.md](./auth/login.md) |
| POST | `/auth/refresh/` | [refresh.md](./auth/refresh.md) |
| POST | `/auth/logout/` | [logout.md](./auth/logout.md) |
| POST | `/auth/google/` | [google.md](./auth/google.md) |
| POST | `/auth/password/forgot/` | [password-forgot.md](./auth/password-forgot.md) |
| POST | `/auth/password/verify-code/` | [password-verify-code.md](./auth/password-verify-code.md) |
| POST | `/auth/password/reset/` | [password-reset.md](./auth/password-reset.md) |

## Índice — Admin Auth (Fase 1)

| Método | Ruta | Documento |
|--------|------|-----------|
| POST | `/admin/auth/login/` | [admin/auth/login.md](./admin/auth/login.md) |
| POST | `/admin/auth/logout/` | [admin/auth/logout.md](./admin/auth/logout.md) |
