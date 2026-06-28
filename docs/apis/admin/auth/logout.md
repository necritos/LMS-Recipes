# POST /api/v1/admin/auth/logout/

Cierra sesión del staff invalidando el refresh token.

## Request

```http
POST /api/v1/admin/auth/logout/
Authorization: Bearer <access_staff>
Content-Type: application/json
```

```json
{
  "refresh": "<jwt_refresh>"
}
```

## Response 200

```json
{
  "data": {
    "message": "Sesión cerrada correctamente."
  },
  "meta": {}
}
```

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 400 | `INVALID_TOKEN` | Refresh inválido |
| 403 | — | Token de usuario (`type=user`) no autorizado |
