# POST /api/v1/auth/password/verify-code/

Verifica que el código OTP es válido antes de cambiar la contraseña.

## Request

```http
POST /api/v1/auth/password/verify-code/
Content-Type: application/json
```

```json
{
  "email": "usuario@ejemplo.com",
  "code": "123456"
}
```

## Response 200

```json
{
  "data": {
    "valid": true
  },
  "meta": {}
}
```

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 422 | `INVALID_CODE` | Código incorrecto |
| 422 | `CODE_EXPIRED` | Código expirado |
| 422 | `CODE_MAX_ATTEMPTS` | Demasiados intentos |
| 429 | `RESEND_TOO_SOON` | Reenvío demasiado pronto |
