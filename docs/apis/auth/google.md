# POST /api/v1/auth/google/

Login o registro con Google OAuth. El frontend obtiene el `id_token` de Google Sign-In y lo envía al backend para verificación.

## Request

```http
POST /api/v1/auth/google/
Content-Type: application/json
```

```json
{
  "id_token": "<google_id_token>"
}
```

## Response 200 (usuario existente)

```json
{
  "data": {
    "access": "<jwt_access>",
    "refresh": "<jwt_refresh>",
    "created": false,
    "user": {
      "id": "uuid",
      "email": "usuario@gmail.com",
      "first_name": "Ana",
      "last_name": "García",
      "status": "active",
      "email_verified": true
    }
  },
  "meta": {}
}
```

## Response 201 (usuario nuevo)

Igual estructura con `"created": true`.

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 401 | `INVALID_GOOGLE_TOKEN` | Token inválido o expirado |
| 422 | `EMAIL_NOT_VERIFIED` | Email de Google no verificado |
| 403 | `ACCOUNT_SUSPENDED` | Cuenta suspendida |
| 503 | `GOOGLE_NOT_CONFIGURED` | Google OAuth no configurado (admin ni env) |

## Notas

- Client ID desde admin: `GET/PATCH /api/v1/admin/site/google/` (guía: [configurar-integraciones.md](../../configurar-integraciones.md) §5).
- El frontend puede leer `GET /api/v1/public/google-oauth/` → `{ enabled, client_id }`.
- Fallback legacy: `GOOGLE_CLIENT_ID` en `.env` solo si `google_oauth_enabled` es `false`.
- Si el email ya existe sin `google_id`, se vincula la cuenta.
