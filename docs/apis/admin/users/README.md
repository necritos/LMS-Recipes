# Admin — Usuarios

Listado y detalle de **usuarios finales** (`UserAccount`). No incluye staff (`StaffUser`).

**Prefijo:** `/api/v1/admin/users/`  
**Auth:** JWT `type=staff`

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/users/` | Listado paginado |
| GET | `/users/{id}/` | Detalle de usuario |

> El historial de compras (`purchases`) se implementará en Fase 5 (commerce). Por ahora el detalle devuelve `purchases: []`.

## Listar usuarios

```http
GET /api/v1/admin/users/?search=maria&status=active&page=1&page_size=20
Authorization: Bearer <access_staff>
```

### Query params

| Param | Descripción |
|-------|-------------|
| `search` | Filtra por email, nombre o apellido (parcial, case-insensitive) |
| `status` | `active` o `suspended` |
| `page` | Página (default 1) |
| `page_size` | Resultados por página (default 20, máx. 100) |

### Response 200

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/v1/admin/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "first_name": "María",
      "last_name": "García",
      "full_name": "María García",
      "status": "active",
      "auth_providers": ["email", "google"],
      "email_verified_at": "2026-06-01T10:00:00Z",
      "last_login": "2026-06-28T08:30:00Z",
      "created_at": "2026-05-15T12:00:00Z",
      "updated_at": "2026-06-28T08:30:00Z"
    }
  ]
}
```

## Detalle de usuario

```http
GET /api/v1/admin/users/{uuid}/
Authorization: Bearer <access_staff>
```

### Response 200

```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "María",
    "last_name": "García",
    "full_name": "María García",
    "status": "active",
    "auth_providers": ["email"],
    "email_verified_at": null,
    "last_login": null,
    "created_at": "2026-05-15T12:00:00Z",
    "updated_at": "2026-05-15T12:00:00Z",
    "purchases": []
  },
  "meta": {}
}
```

### `auth_providers`

| Valor | Significado |
|-------|-------------|
| `email` | Registro con email/contraseña |
| `google` | Vinculado con Google OAuth |

## Errores

| HTTP | Cuándo |
|------|--------|
| 401 | Sin token o token de usuario (no staff) |
| 404 | UUID inexistente |

## Notas

- Los usuarios se crean vía `POST /api/v1/auth/register/` o `POST /api/v1/auth/google/`.
- Staff se gestiona por Django admin / `createsuperuser`, no por esta API.
