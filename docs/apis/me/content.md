# Me — Contenido con acceso

JWT `type=user`. Requiere un `AccessGrant` activo (lo crea el webhook de Stripe al pagar; también se puede crear en Django admin / tests).

Query `?lang=es` (default `es`) para textos traducidos.

## GET `/api/v1/me/courses/{id}/lessons/`

Temario con descripción de módulo/lección, **contenido HTML** de la lección y URL firmada de Bunny. No incluye `bunny_video_id`.

```json
{
  "data": {
    "course_id": "uuid",
    "modules": [
      {
        "id": "uuid",
        "title": "Introducción",
        "description": "Qué verás en este módulo",
        "sort_order": 0,
        "lessons": [
          {
            "id": "uuid",
            "title": "Bienvenida",
            "description": "Resumen corto",
            "content_html": "<p>Texto rico de la lección…</p>",
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

En el **catálogo público** el temario solo trae `title` + `description` (sin `content_html` ni video).

## GET `/api/v1/me/recipes/{id}/`

Detalle de receta **solo con compra**: ingredientes y preparación (HTML por idioma) + video firmado.

```json
{
  "data": {
    "id": "uuid",
    "slug": "receta-tiramisu",
    "title": "Tiramisú clásico",
    "description": "Teaser / resumen",
    "ingredients_html": "<ul><li>Mascarpone</li></ul>",
    "preparation_html": "<ol><li>Batir…</li></ol>",
    "video": {
      "signed_video_url": "https://iframe.mediadelivery.net/embed/…",
      "hls_url": "https://vz-xxx.b-cdn.net/…/playlist.m3u8?…",
      "expires_at": "2026-08-14T19:00:00Z"
    }
  },
  "meta": {}
}
```

`ingredients_html` y `preparation_html` **no** salen en `GET /public/recipes/…`.

## GET `/api/v1/me/recipes/{id}/video/`

Solo el bloque `video` (compatibilidad). Preferible el detalle de arriba.

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 401 | — | Sin JWT de usuario |
| 403 | `ACCESS_DENIED` | Sin compra / grant |
| 403 | `ACCESS_EXPIRED` | Grant con `expires_at` pasado |
| 404 | `COURSE_NOT_FOUND` / `RECIPE_NOT_FOUND` | ID inexistente |
| 404 | `VIDEO_NOT_FOUND` | Receta/lección sin `bunny_video_id` (en endpoints de video) |
| 503 | `BUNNY_NOT_CONFIGURED` | Bunny no activado en admin |
