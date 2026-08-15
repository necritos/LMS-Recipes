# Admin — Módulos y lecciones

Estructura de un curso. Textos por idioma. El `bunny_video_id` es global (un video por lección).

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
    {
      "language_code": "es",
      "title": "Introducción",
      "description": "Qué aprenderás en este módulo"
    },
    {
      "language_code": "sk",
      "title": "Úvod",
      "description": "Čo sa naučíte v tomto module"
    }
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
    {
      "language_code": "es",
      "title": "Bienvenida",
      "description": "Resumen de la lección",
      "content_html": "<p>Contenido rico…</p>"
    },
    {
      "language_code": "sk",
      "title": "Vitajte",
      "description": "Súhrn lekcie",
      "content_html": "<p>Obsah…</p>"
    }
  ]
}
```

| Campo traducción | Dónde se ve |
|------------------|-------------|
| `title` | Público + me |
| `description` (módulo/lección) | Público (temario) + me |
| `content_html` (lección) | **Solo** `GET /me/courses/{id}/lessons/` (con acceso) |

`bunny_video_id` se puede dejar vacío y asignar después con `PATCH /admin/lessons/{id}/`.

En recetas: `PATCH /admin/recipes/{slug}/` con `{ "bunny_video_id": "..." }` e `ingredients_html` / `preparation_html` en traducciones.

El catálogo público lista el temario **sin** `bunny_video_id` ni `content_html`. Las URLs firmadas y el HTML de lección solo salen en `/api/v1/me/`.
