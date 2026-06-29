# GET /api/v1/public/categories/

Categorías activas con nombre traducido.

## Query params

| Param | Descripción |
|-------|-------------|
| `lang` | Código de idioma (default: `es`) |

## Response 200

```json
{
  "data": [
    {
      "id": "uuid",
      "slug": "cocina",
      "name": "Cocina",
      "description": "",
      "sort_order": 0
    }
  ],
  "meta": {}
}
```
