# Me — Contenido con acceso

JWT `type=user`. Requiere un `AccessGrant` activo (lo crea el webhook de Stripe al pagar; también se puede crear en Django admin / tests).

Query `?lang=es` (default `es`) para títulos de módulos y lecciones.

## GET `/api/v1/me/courses/{id}/lessons/`

Devuelve el temario con URL firmada de Bunny **por lección**. No incluye `bunny_video_id` como campo.

```json
{
  "data": {
    "course_id": "uuid",
    "modules": [
      {
        "id": "uuid",
        "title": "Introducción",
        "sort_order": 0,
        "lessons": [
          {
            "id": "uuid",
            "title": "Bienvenida",
            "duration_seconds": 90,
            "sort_order": 0,
            "video": {
              "signed_video_url": "https://iframe.mediadelivery.net/embed/123/…?token=…&expires=…",
              "hls_url": "https://vz-xxx.b-cdn.net/…/playlist.m3u8?token=…&expires=…",
              "expires_at": "2026-08-14T19:00:00Z"
            }
          }
        ]
      }
    ]
  },
  "meta": {}
}
```

Si la lección no tiene video: `"video": null`.

## GET `/api/v1/me/recipes/{id}/video/`

```json
{
  "data": {
    "recipe_id": "uuid",
    "video": {
      "signed_video_url": "https://iframe.mediadelivery.net/embed/…",
      "hls_url": "https://vz-xxx.b-cdn.net/…/playlist.m3u8?…",
      "expires_at": "2026-08-14T19:00:00Z"
    }
  },
  "meta": {}
}
```

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 401 | — | Sin JWT de usuario |
| 403 | `ACCESS_DENIED` | Sin compra / grant |
| 403 | `ACCESS_EXPIRED` | Grant con `expires_at` pasado |
| 404 | `COURSE_NOT_FOUND` / `RECIPE_NOT_FOUND` | ID inexistente |
| 404 | `VIDEO_NOT_FOUND` | Receta sin `bunny_video_id` |
| 503 | `BUNNY_NOT_CONFIGURED` | Bunny no activado en admin |
