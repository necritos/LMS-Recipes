# Admin — Catálogo

CRUD de idiomas, categorías, cursos y recetas. Requiere JWT `type=staff`.

**Prefijo:** `/api/v1/admin/`

## Documentación por recurso

| Recurso | Guía | Endpoints |
|---------|------|-----------|
| **Idiomas** | [languages.md](./languages.md) — **lee esto primero** para entender multi-idioma | `GET/POST /languages/`, `GET/PATCH/DELETE /languages/{code}/` |
| **Categorías** | [categories.md](./categories.md) | `GET/POST /categories/`, `GET/PATCH/DELETE /categories/{slug}/` |
| **Cursos** | [courses.md](./courses.md) | `GET/POST /courses/`, `GET/PATCH/DELETE /courses/{slug}/` |
| **Recetas** | [recipes.md](./recipes.md) | `GET/POST /recipes/`, `GET/PATCH/DELETE /recipes/{slug}/` |

## Resumen multi-idioma

1. **Idiomas** (`Language`) — catálogo de códigos disponibles (`es`, `en`…).
2. **Traducciones** — cada categoría/curso/receta lleva un array `translations` con `language_code`.
3. **Público** — el frontend pasa `?lang=es`; solo se muestra contenido con traducción en ese idioma.
4. **Activación** — desactivar un idioma (`is_active=false`) lo oculta del sitio sin borrar traducciones.

Detalle completo: [languages.md](./languages.md).

## Referencia rápida

Ver [catalog-crud.md](./catalog-crud.md) para ejemplos JSON compactos y tabla de errores comunes.
