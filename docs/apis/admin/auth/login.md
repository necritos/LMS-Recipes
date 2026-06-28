# POST /api/v1/admin/auth/login/

Inicio de sesión del panel administrativo (staff).

## Request

```http
POST /api/v1/admin/auth/login/
Content-Type: application/json
```

```json
{
  "email": "admin@recetario.local",
  "password": "claveAdminSegura"
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
      "email": "admin@recetario.local",
      "first_name": "Admin",
      "last_name": "Recetario"
    }
  },
  "meta": {}
}
```

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 401 | `INVALID_CREDENTIALS` | Credenciales incorrectas |

## Notas

- JWT incluye `type: "staff"`.
- Crear staff: `python manage.py createsuperuser` o Django admin.
