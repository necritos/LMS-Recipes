# Me — Biblioteca (cursos y recetas con acceso)

JWT `type=user`. Solo **accesos activos** (no revocados y no vencidos).  
Títulos con `?lang=es`. Listas paginadas.

Cursos: acceso 365 días desde la compra (salvo que el producto tenga otro `access_days`).  
Recetas: `lifetime` (`expires_at: null`) o temporal según el producto.

## GET `/me/courses/`

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "product_id": "uuid",
      "slug": "curso-pasta",
      "title": "Curso de Pasta",
      "cover_image_url": null,
      "expires_at": "2027-08-14T18:00:00Z",
      "is_lifetime": false,
      "is_active": true,
      "access_days": 365,
      "continue_lesson": {
        "id": "uuid",
        "module_id": "uuid",
        "title": "Bienvenida",
        "sort_order": 0
      }
    }
  ]
}
```

`continue_lesson` es la última lección con `POST /me/lessons/{id}/view/` (o `complete/`); si no hay progreso, la primera lección del curso. `null` si el curso no tiene lecciones.

Un grant vencido **no** aparece aquí; el video responde `403 ACCESS_EXPIRED`.

## GET `/me/recipes/`

Igual, sin `continue_lesson`. Incluye `access_type` (`lifetime` \| `timed`) y `access_days`.
