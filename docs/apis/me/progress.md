# Me — Progreso y continuar viendo

JWT `type=user`. Requiere `AccessGrant` activo del curso (`403 ACCESS_DENIED` / `ACCESS_EXPIRED`).

## POST `/me/lessons/{id}/view/`

Registra la última lección vista (continuar viendo). No marca completada.

## POST `/me/lessons/{id}/complete/`

Marca la lección como completada (idempotente) y actualiza `last_viewed_at`.

```json
{
  "data": {
    "lesson_id": "uuid",
    "completed": true,
    "completed_at": "2026-08-14T19:00:00Z",
    "last_viewed_at": "2026-08-14T19:00:00Z"
  },
  "meta": {}
}
```

## GET `/me/progress/{course_id}/`

```json
{
  "data": {
    "course_id": "uuid",
    "total_lessons": 10,
    "completed_lessons": 3,
    "percent": 30,
    "continue_lesson": {
      "id": "uuid",
      "module_id": "uuid",
      "title": "Salsas",
      "sort_order": 2
    },
    "lessons": [
      {
        "id": "uuid",
        "module_id": "uuid",
        "title": "Bienvenida",
        "sort_order": 0,
        "duration_seconds": 90,
        "completed": true,
        "completed_at": "2026-08-14T19:00:00Z",
        "last_viewed_at": "2026-08-14T19:00:00Z"
      }
    ]
  },
  "meta": {}
}
```

`continue_lesson` también va en `GET /me/courses/`.
