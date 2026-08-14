# Admin — Newsletter

Emails de `POST /api/v1/public/newsletter/`.

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/newsletter/` | Listado paginado. `?search=` filtra email |
| GET | `/newsletter/{id}/` | Detalle |
| DELETE | `/newsletter/{id}/` | Baja |

Por ahora solo se almacenan; no hay envío masivo.
