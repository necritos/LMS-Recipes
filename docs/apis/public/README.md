# Public — Catálogo y sitio

Endpoints públicos (sin autenticación).

## Catálogo

| Endpoint | Documento |
|----------|-----------|
| GET `/public/languages/` | [languages.md](./languages.md) |
| GET `/public/categories/` | [categories.md](./categories.md) |
| GET `/public/courses/` | [courses.md](./courses.md) — `?course_format=online\|in_person` |
| GET `/public/courses/{slug}/` | [course-detail.md](./course-detail.md) |
| GET `/public/recipes/` | [recipes.md](./recipes.md) |
| GET `/public/recipes/{slug}/` | [recipe-detail.md](./recipe-detail.md) |

Query param común: `?lang=es` (default: `es`). Incluye catálogo y `GET /public/site/`.

Guía multi-idioma: [../admin/catalog/languages.md](../admin/catalog/languages.md).

## Sitio / home

| Endpoint | Documento |
|----------|-----------|
| GET `/public/site/` | [site.md](./site.md) |
| GET `/public/google-oauth/` | Client ID público para el botón Google ([configurar-integraciones §5](../../configurar-integraciones.md)) |
| POST `/public/contact/` | [contact.md](./contact.md) |
| POST `/public/newsletter/` | [newsletter.md](./newsletter.md) — guía frontend: [frontend-newsletter.md](../../frontend-newsletter.md) |
