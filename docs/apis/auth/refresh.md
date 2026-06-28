# POST /api/v1/auth/refresh/

Renueva el access token usando el refresh token.

## Request

```http
POST /api/v1/auth/refresh/
Content-Type: application/json
```

```json
{
  "refresh": "<jwt_refresh>"
}
```

## Response 200

Respuesta estándar de SimpleJWT (envuelta por el renderer si aplica):

```json
{
  "data": {
    "access": "<nuevo_jwt_access>",
    "refresh": "<nuevo_jwt_refresh>"
  },
  "meta": {}
}
```

## Notas

- Con `ROTATE_REFRESH_TOKENS=True`, se emite un nuevo refresh token y el anterior queda en blacklist.
