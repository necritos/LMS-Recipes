# GET /api/v1/public/courses/{slug}/

Detalle de un curso publicado.

## Query params

| Param | Descripción |
|-------|-------------|
| `lang` | Código de idioma (default: `es`) |

## Response 200

Incluye campos SEO: `meta_title`, `meta_description`.

`modules` lista el temario (títulos por `?lang=`) **sin** IDs de video. Las URLs firmadas están en [`GET /me/courses/{id}/lessons/`](../me/content.md).

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 404 | `COURSE_NOT_FOUND` | Slug inexistente o sin traducción en ese idioma |
