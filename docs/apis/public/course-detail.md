# GET /api/v1/public/courses/{slug}/

Detalle de un curso publicado.

## Query params

| Param | Descripción |
|-------|-------------|
| `lang` | Código de idioma (default: `es`) |

## Response 200

Incluye campos SEO: `meta_title`, `meta_description`.

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 404 | `COURSE_NOT_FOUND` | Slug inexistente o sin traducción en ese idioma |
