# Admin — Recetas

CRUD de recetas vendibles con traducciones, imagen de portada y tipos de acceso.

**Prefijo:** `/api/v1/admin/recipes/`  
**Auth:** JWT `type=staff`

Ver también: [Idiomas y multi-idioma](./languages.md)

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/recipes/` | Listar |
| POST | `/recipes/` | Crear |
| GET | `/recipes/{slug}/` | Detalle |
| PATCH | `/recipes/{slug}/` | Actualizar |
| DELETE | `/recipes/{slug}/` | Eliminar |

## Crear receta — acceso lifetime

```http
POST /api/v1/admin/recipes/
Content-Type: application/json
```

```json
{
  "slug": "receta-tiramisu",
  "price": "12.99",
  "category_id": null,
  "access_type": "lifetime",
  "status": "published",
  "sort_order": 0,
  "translations": [
    {
      "language_code": "es",
      "title": "Tiramisú clásico",
      "description": "Receta paso a paso",
      "meta_title": "Tiramisú — Recetario",
      "meta_description": "Aprende a hacer tiramisú"
    },
    {
      "language_code": "en",
      "title": "Classic Tiramisu",
      "description": "Step by step recipe",
      "meta_title": "Tiramisu — Recetario",
      "meta_description": "Learn to make tiramisu"
    }
  ]
}
```

## Acceso limitado (365 días)

```json
{
  "slug": "receta-premium",
  "price": "14.99",
  "access_type": "timed",
  "access_days": 365,
  "status": "published",
  "translations": [
    { "language_code": "es", "title": "Receta premium", "description": "…" }
  ]
}
```

| `access_type` | `access_days` | Comportamiento |
|---------------|---------------|----------------|
| `lifetime` | ignorado / null | Acceso permanente tras compra |
| `timed` | obligatorio (ej. 365) | Acceso expira N días después de la compra (Fase 5) |

## Subir imagen de portada

```http
PATCH /api/v1/admin/recipes/{slug}/
Content-Type: multipart/form-data

cover_image=<archivo>
```

También en `POST` multipart junto con campos JSON (`translations` como string).

## Campos

| Campo | Tipo | Notas |
|-------|------|-------|
| `slug` | string | Único |
| `category_id` | uuid \| null | Categoría opcional |
| `price` | decimal | Precio de venta |
| `access_type` | `lifetime` \| `timed` | Modelo de acceso |
| `access_days` | int \| null | Requerido si `timed` |
| `status` | `draft` \| `published` | Solo `published` en catálogo público |
| `sort_order` | int | Orden en listados |
| `cover_image` | file | Imagen de portada |
| `translations` | array | Al menos una traducción |

## Catálogo público

```http
GET /api/v1/public/recipes/?lang=es&category=postres&search=tiramisu
GET /api/v1/public/recipes/receta-tiramisu/?lang=es
```

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 409 | `SLUG_ALREADY_EXISTS` | Slug duplicado |
| 422 | `TRANSLATIONS_REQUIRED` | Sin traducciones |
| 422 | `LANGUAGE_NOT_FOUND` | Idioma inválido |
| 422 | `ACCESS_DAYS_REQUIRED` | `timed` sin `access_days` |
