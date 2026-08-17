# Admin — Cursos

CRUD de cursos con traducciones, imagen de portada y acceso de 365 días por defecto.

Hay dos formatos:

| `format` | Qué es | Módulos / recursos | Extra |
|----------|--------|--------------------|-------|
| `online` | LMS actual (default) | Sí | — |
| `in_person` | Taller o clase presencial | No | `event_starts_at`, `event_address`, `maps_url` |

Ambos se compran igual (carrito → Stripe → `AccessGrant`).

**Prefijo:** `/api/v1/admin/courses/`  
**Auth:** JWT `type=staff`

Ver también: [Idiomas y multi-idioma](./languages.md) · [Recursos](./resources.md)

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/courses/` | Listar |
| POST | `/courses/` | Crear |
| GET | `/courses/{slug}/` | Detalle |
| PATCH | `/courses/{slug}/` | Actualizar |
| DELETE | `/courses/{slug}/` | Eliminar |
| GET | `/courses/{slug}/purchases/` | Compradores (paginado) |
| GET/POST | `/courses/{slug}/resources/` | Recursos del curso online — [resources.md](./resources.md) |

## Crear curso bilingüe (online)

```http
POST /api/v1/admin/courses/
Content-Type: application/json
```

```json
{
  "slug": "curso-pasta",
  "price": "49.99",
  "access_days": 365,
  "format": "online",
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

Si omites `format`, se crea como `online`.

## Crear curso presencial

Obligatorios: `event_starts_at` (fecha y hora), `event_address`, `maps_url`.

```json
{
  "slug": "taller-madrid",
  "price": "79.00",
  "format": "in_person",
  "event_starts_at": "2026-09-15T18:00:00Z",
  "event_address": "Calle Mayor 1, Madrid",
  "maps_url": "https://maps.google.com/?q=Calle+Mayor+1+Madrid",
  "status": "published",
  "translations": [
    {
      "language_code": "es",
      "title": "Taller de pasta en Madrid",
      "description": "Clase presencial de 3 horas"
    }
  ]
}
```

No se pueden crear módulos ni recursos en un presencial (`IN_PERSON_NO_CURRICULUM` / `IN_PERSON_NO_RESOURCES`). Para pasar un online a presencial hay que borrar antes módulos y recursos (`IN_PERSON_HAS_CONTENT`).

## Lista de compras

Pensado sobre todo para presenciales (asistencia), pero funciona en cualquier curso.

```http
GET /api/v1/admin/courses/{slug}/purchases/?page=1&page_size=20
Authorization: Bearer <access_staff>
```

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "user": {
        "id": "uuid",
        "email": "user@example.com",
        "first_name": "María",
        "last_name": "García",
        "full_name": "María García"
      },
      "order_id": "uuid",
      "paid_at": "2026-08-14T10:00:00Z",
      "created_at": "2026-08-14T10:00:00Z",
      "expires_at": "2027-08-14T10:00:00Z",
      "is_lifetime": false
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
| `format` | `online` \| `in_person` | Default `online` |
| `event_starts_at` | datetime \| null | Obligatorio si presencial |
| `event_address` | string | Dirección del evento (presencial) |
| `maps_url` | url | Enlace de Google Maps (presencial) |
| `status` | `draft` \| `published` | Borrador oculto en público |
| `sort_order` | int | Orden en listados |
| `cover_image` | file | Imagen de portada |
| `translations` | array | Al menos una traducción |

## Catálogo público

```http
GET /api/v1/public/courses/?lang=es&category=postres&search=pasta
GET /api/v1/public/courses/?lang=es&course_format=in_person
GET /api/v1/public/courses/taller-madrid/?lang=es
```

El detalle público de un presencial trae fecha, dirección y Maps, y `modules: []`.

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 409 | `SLUG_ALREADY_EXISTS` | Slug duplicado |
| 422 | `TRANSLATIONS_REQUIRED` | Sin traducciones |
| 422 | `LANGUAGE_NOT_FOUND` | Idioma inválido |
| 422 | `IN_PERSON_EVENT_REQUIRED` | Presencial sin fecha, dirección o Maps |
| 422 | `IN_PERSON_HAS_CONTENT` | Pasar a presencial con módulos o recursos |

