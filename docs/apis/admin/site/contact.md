# Admin — Mensajes de contacto

Inbox de `POST /api/v1/public/contact/`.

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/contact/` | Listado paginado. `?is_read=true\|false` |
| GET | `/contact/{id}/` | Detalle |
| PATCH | `/contact/{id}/` | `{ "is_read": true }` o `false` |
| DELETE | `/contact/{id}/` | Eliminar |

Orden: no leídos primero, luego más recientes.
