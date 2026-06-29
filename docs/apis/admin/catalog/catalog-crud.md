# Admin — Referencia rápida CRUD catálogo

Autenticación: `Authorization: Bearer <access_staff>`

Documentación detallada por recurso:

- [Idiomas y multi-idioma](./languages.md)
- [Categorías](./categories.md)
- [Cursos](./courses.md)
- [Recetas](./recipes.md)

## Crear curso (bilingüe)

```http
POST /api/v1/admin/courses/
Content-Type: application/json
```

```json
{
  "slug": "curso-pasta",
  "price": "49.99",
  "access_days": 365,
  "category_id": null,
  "status": "published",
  "sort_order": 0,
  "translations": [
    {
      "language_code": "es",
      "title": "Curso de Pasta",
      "description": "Descripción en español",
      "meta_title": "SEO título ES",
      "meta_description": "SEO descripción ES"
    },
    {
      "language_code": "en",
      "title": "Pasta Course",
      "description": "English description",
      "meta_title": "SEO title EN",
      "meta_description": "SEO description EN"
    }
  ]
}
```

## Crear categoría

```json
{
  "slug": "postres",
  "translations": [
    { "language_code": "es", "name": "Postres", "description": "…" },
    { "language_code": "en", "name": "Desserts", "description": "…" }
  ]
}
```

## Crear receta

```json
{
  "slug": "receta-tiramisu",
  "price": "12.99",
  "access_type": "lifetime",
  "status": "published",
  "translations": [
    { "language_code": "es", "title": "Tiramisú", "description": "..." }
  ]
}
```

Acceso limitado: `"access_type": "timed", "access_days": 365`

## Subir imagen de portada

```http
PATCH /api/v1/admin/courses/{slug}/
Content-Type: multipart/form-data

cover_image=<archivo>
```

Igual para `/admin/recipes/{slug}/`. En multipart, `translations` como string JSON.

## Errores comunes

| HTTP | code | Cuándo |
|------|------|--------|
| 409 | `SLUG_ALREADY_EXISTS` | Slug duplicado |
| 409 | `LANGUAGE_ALREADY_EXISTS` | Código de idioma duplicado |
| 422 | `TRANSLATIONS_REQUIRED` | Sin traducciones |
| 422 | `LANGUAGE_NOT_FOUND` | Código de idioma inválido |
| 422 | `ACCESS_DAYS_REQUIRED` | Receta timed sin access_days |
