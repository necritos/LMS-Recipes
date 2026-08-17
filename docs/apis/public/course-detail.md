# GET /api/v1/public/courses/{slug}/

Detalle de un curso publicado.

## Query params

| Param | Descripción |
|-------|-------------|
| `lang` | Código de idioma (default: `es`) |

## Response 200

Incluye el mismo `format` que el listado (`online` \| `in_person`), más campos SEO: `meta_title`, `meta_description`.

`modules` lista el temario (títulos por `?lang=`) **sin** IDs de video. Las URLs firmadas están en [`GET /me/courses/{id}/lessons/`](../me/content.md).

Si `format` es `in_person`, `modules` va vacío y el detalle incluye `event_starts_at`, `event_address` y `maps_url`. Los recursos descargables **no** salen en público (solo [`/me/courses/{id}/resources/`](../me/content.md) tras comprar).

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 404 | `COURSE_NOT_FOUND` | Slug inexistente o sin traducción en ese idioma |
