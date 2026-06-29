# Admin — Cursos

CRUD de cursos con traducciones, imagen de portada y acceso de 365 días por defecto.

**Prefijo:** `/api/v1/admin/courses/`  
**Auth:** JWT `type=staff`

Ver también: [Idiomas y multi-idioma](./languages.md)

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/courses/` | Listar |
| POST | `/courses/` | Crear |
| GET | `/courses/{slug}/` | Detalle |
| PATCH | `/courses/{slug}/` | Actualizar |
| DELETE | `/courses/{slug}/` | Eliminar |

## Crear curso bilingüe

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

## Subir imagen de portada

```http
PATCH /api/v1/admin/courses/{slug}/
Content-Type: multipart/form-data

cover_image=<archivo>
```

En multipart, enviar `translations` como string JSON si se actualizan traducciones a la vez.

## Campos

| Campo | Tipo | Notas |
|-------|------|-------|
| `slug` | string | Único |
| `category_id` | uuid \| null | Categoría opcional |
| `price` | decimal | Precio de venta |
| `access_days` | int | Días de acceso tras compra (default 365) |
| `status` | `draft` \| `published` | Borrador oculto en público |
| `sort_order` | int | Orden en listados |
| `cover_image` | file | Imagen de portada |
| `translations` | array | Al menos una traducción |

## Catálogo público

```http
GET /api/v1/public/courses/?lang=es&category=postres&search=pasta
GET /api/v1/public/courses/curso-pasta/?lang=es
```

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 409 | `SLUG_ALREADY_EXISTS` | Slug duplicado |
| 422 | `TRANSLATIONS_REQUIRED` | Sin traducciones |
| 422 | `LANGUAGE_NOT_FOUND` | Idioma inválido |
