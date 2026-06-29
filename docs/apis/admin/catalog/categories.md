# Admin — Categorías

CRUD de categorías con traducciones multi-idioma.

**Prefijo:** `/api/v1/admin/categories/`  
**Auth:** JWT `type=staff`

Ver también: [Idiomas y multi-idioma](./languages.md)

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/categories/` | Listar (incluye todas las traducciones) |
| POST | `/categories/` | Crear |
| GET | `/categories/{slug}/` | Detalle |
| PATCH | `/categories/{slug}/` | Actualizar |
| DELETE | `/categories/{slug}/` | Eliminar |

## Crear categoría

```http
POST /api/v1/admin/categories/
Content-Type: application/json
```

```json
{
  "slug": "postres",
  "sort_order": 10,
  "is_active": true,
  "translations": [
    {
      "language_code": "es",
      "name": "Postres",
      "description": "Categoría de postres y dulces"
    },
    {
      "language_code": "en",
      "name": "Desserts",
      "description": "Desserts and sweets category"
    }
  ]
}
```

**Response 201** — objeto categoría con array `translations`.

## Actualizar traducciones

`PATCH` con `translations` **reemplaza** todas las traducciones existentes:

```json
{
  "translations": [
    { "language_code": "es", "name": "Postres y dulces", "description": "…" },
    { "language_code": "en", "name": "Desserts", "description": "…" },
    { "language_code": "fr", "name": "Desserts", "description": "…" }
  ]
}
```

## Campos

| Campo | Tipo | Notas |
|-------|------|-------|
| `slug` | string | Único, URL-friendly |
| `sort_order` | int | Orden en listados |
| `is_active` | bool | Si `false`, no aparece en catálogo público |
| `translations[].language_code` | string | Debe existir en `/admin/languages/` |
| `translations[].name` | string | Nombre visible (no usar `title`) |
| `translations[].description` | string | Opcional |

## Catálogo público

```http
GET /api/v1/public/categories/?lang=es
```

Solo categorías activas con traducción en el idioma solicitado.

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 409 | `SLUG_ALREADY_EXISTS` | Slug duplicado |
| 422 | `TRANSLATIONS_REQUIRED` | Array vacío |
| 422 | `LANGUAGE_NOT_FOUND` | Código de idioma inválido |
