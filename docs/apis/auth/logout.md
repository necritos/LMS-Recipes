# POST /api/v1/auth/logout/

Invalida el refresh token (blacklist).

## Request

```http
POST /api/v1/auth/logout/
Authorization: Bearer <access>
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
| 400 | `INVALID_TOKEN` | Refresh token inválido |
| 401 | — | Sin autenticación |
