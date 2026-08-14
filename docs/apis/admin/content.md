# Admin — Módulos y lecciones

Estructura de un curso. Títulos por idioma. El `bunny_video_id` es global (un video por lección).

**Auth:** JWT `type=staff`

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/admin/courses/{slug}/modules/` | Listar módulos del curso (con lecciones) |
| POST | `/admin/courses/{slug}/modules/` | Crear módulo |
| GET/PATCH/DELETE | `/admin/modules/{id}/` | Detalle / editar / borrar módulo |
| GET | `/admin/modules/{id}/lessons/` | Listar lecciones |
| POST | `/admin/modules/{id}/lessons/` | Crear lección |
| GET/PATCH/DELETE | `/admin/lessons/{id}/` | Detalle / editar / borrar lección |

## Crear módulo

```json
{
  "sort_order": 0,
  "is_active": true,
  "translations": [
    { "language_code": "es", "title": "Introducción" },
    { "language_code": "en", "title": "Introduction" }
  ]
}
```

## Crear lección

```json
{
  "bunny_video_id": "guid-de-bunny-stream",
  "duration_seconds": 420,
  "sort_order": 0,
  "is_active": true,
  "translations": [
    { "language_code": "es", "title": "Bienvenida" },
    { "language_code": "en", "title": "Welcome" }
  ]
}
```

`bunny_video_id` se puede dejar vacío y asignar después con `PATCH /admin/lessons/{id}/`.

En recetas: `PATCH /admin/recipes/{slug}/` con `{ "bunny_video_id": "..." }`.

El catálogo público lista el temario **sin** `bunny_video_id`. Las URLs firmadas solo salen en `/api/v1/me/`.
