# Public — Catálogo

Endpoints públicos del catálogo (sin autenticación).

| Endpoint | Documento |
|----------|-----------|
| GET `/public/languages/` | [languages.md](./languages.md) |
| GET `/public/categories/` | [categories.md](./categories.md) |
| GET `/public/courses/` | [courses.md](./courses.md) |
| GET `/public/courses/{slug}/` | [course-detail.md](./course-detail.md) |
| GET `/public/recipes/` | [recipes.md](./recipes.md) |
| GET `/public/recipes/{slug}/` | [recipe-detail.md](./recipe-detail.md) |

Query param común: `?lang=es` (default: `es`).

Guía completa del sistema multi-idioma (modelo, traducciones, activación): [../admin/catalog/languages.md](../admin/catalog/languages.md).
