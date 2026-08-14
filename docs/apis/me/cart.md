# Me — Carrito

JWT `type=user`. Prefijo `/api/v1/me/`.

Títulos según `?lang=es` (default `es`).

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/me/cart/` | Ver carrito |
| POST | `/me/cart/` | Añadir curso o receta |
| DELETE | `/me/cart/` | Vaciar |
| DELETE | `/me/cart/items/{id}/` | Quitar un ítem |

## Añadir

```json
{ "course_id": "uuid" }
```

o

```json
{ "recipe_id": "uuid" }
```

Solo productos `published`. Un mismo producto no se duplica (`409 ITEM_ALREADY_IN_CART`).

## Response

```json
{
  "data": {
    "id": "uuid",
    "items": [
      {
        "id": "uuid",
        "product_type": "course",
        "product_id": "uuid",
        "slug": "curso-pasta",
        "title": "Curso de Pasta",
        "price": "49.99"
      }
    ],
    "total": "49.99",
    "currency": "eur"
  },
  "meta": {}
}
```

Tras un pago confirmado por webhook, el carrito se vacía.
