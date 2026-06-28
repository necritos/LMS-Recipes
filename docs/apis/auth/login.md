# POST /api/v1/auth/login/

Inicio de sesión de usuario.

## Request

```http
POST /api/v1/auth/login/
Content-Type: application/json
```

```json
{
  "email": "usuario@ejemplo.com",
  "password": "miClaveSegura"
}
```

## Response 200

```json
{
  "data": {
    "access": "<jwt_access>",
    "refresh": "<jwt_refresh>",
    "user": {
      "id": "uuid",
      "email": "usuario@ejemplo.com",
      "first_name": "Ana",
      "last_name": "García",
      "status": "active",
      "email_verified": false
    }
  },
  "meta": {}
}
```

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 401 | `INVALID_CREDENTIALS` | Email o contraseña incorrectos |
| 403 | `ACCOUNT_SUSPENDED` | Cuenta suspendida |

## Notas

- Header en rutas protegidas: `Authorization: Bearer <access>`
