# POST /api/v1/auth/register/

Registro de usuario con email y contraseña.

## Request

```http
POST /api/v1/auth/register/
Content-Type: application/json
```

```json
{
  "email": "usuario@ejemplo.com",
  "password": "miClaveSegura",
  "password_confirm": "miClaveSegura",
  "first_name": "Ana",
  "last_name": "García",
  "terms_accepted": true
}
```

## Campos

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `email` | string | Sí | Correo único |
| `password` | string | Sí | Mínimo 8 caracteres |
| `password_confirm` | string | Sí | Debe coincidir con `password` |
| `first_name` | string | No | Nombre |
| `last_name` | string | No | Apellido |
| `terms_accepted` | boolean | Sí | Debe ser `true` |

## Response 201

```json
{
  "data": {
    "id": "uuid",
    "email": "usuario@ejemplo.com",
    "first_name": "Ana",
    "last_name": "García",
    "status": "active",
    "email_verified": false,
    "access": "<jwt_access>",
    "refresh": "<jwt_refresh>"
  },
  "meta": {}
}
```

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 409 | `EMAIL_ALREADY_REGISTERED` | Email ya registrado |
| 422 | `TERMS_NOT_ACCEPTED` | Términos no aceptados |
| 422 | `PASSWORD_MISMATCH` | Contraseñas no coinciden |
| 422 | `WEAK_PASSWORD` | Menos de 8 caracteres |

## Notas

- Tras el registro se encola un email de bienvenida (Celery).
- El token JWT incluye `type: "user"`.
