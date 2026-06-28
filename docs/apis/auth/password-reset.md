# POST /api/v1/auth/password/reset/

Restablece la contraseña usando el código OTP verificado.

## Request

```http
POST /api/v1/auth/password/reset/
Content-Type: application/json
```

```json
{
  "email": "usuario@ejemplo.com",
  "code": "123456",
  "password": "nuevaClaveSegura",
  "password_confirm": "nuevaClaveSegura"
}
```

## Response 200

```json
{
  "data": {
    "message": "Contraseña actualizada correctamente."
  },
  "meta": {}
}
```

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 422 | `INVALID_CODE` | Código inválido o expirado |
| 422 | `PASSWORD_MISMATCH` | Contraseñas no coinciden |
| 422 | `WEAK_PASSWORD` | Menos de 8 caracteres |
