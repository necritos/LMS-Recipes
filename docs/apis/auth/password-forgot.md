# POST /api/v1/auth/password/forgot/

Solicita un código OTP de 6 dígitos para restablecer la contraseña.

## Request

```http
POST /api/v1/auth/password/forgot/
Content-Type: application/json
```

```json
{
  "email": "usuario@ejemplo.com"
}
```

## Response 200

Siempre la misma respuesta (evita enumeración de emails):

```json
{
  "data": {
    "message": "Si el correo está registrado, recibirás un código para restablecer tu contraseña."
  },
  "meta": {}
}
```

## Notas

- Código válido 15 minutos.
- Cooldown de reenvío: 60 segundos.
- Máximo 5 intentos de verificación por código.
