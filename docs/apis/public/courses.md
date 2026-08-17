# GET /api/v1/public/courses/

Listado paginado de cursos publicados en el idioma solicitado.

## Query params

| Param | Descripción |
|-------|-------------|
| `lang` | Código de idioma (default: `es`) |
| `category` | Filtrar por slug de categoría |
| `search` | Buscar en título/descripción |
| `course_format` | `online` o `in_person` |
| `page` | Página |
| `page_size` | Tamaño (máx. 100) |

## Response 200

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "slug": "curso-pasta",
      "title": "Curso de Pasta",
      "description": "Aprende pasta italiana",
      "price": "49.99",
      "access_days": 365,
      "format": "online",
      "event_starts_at": null,
      "event_address": "",
      "maps_url": "",
      "category_slug": "cocina",
      "cover_image_url": "http://localhost:8000/media/..."
    }
  ]
}
```
