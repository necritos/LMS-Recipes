# Me — Compras

JWT `type=user`. Prefijo `/api/v1/me/`.

Lista paginada (incluye compras con acceso ya expirado). Títulos con `?lang=es`.

## GET `/me/purchases/`

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "order_id": "uuid",
      "product_type": "course",
      "product_id": "uuid",
      "slug": "curso-pasta",
      "title": "Curso de Pasta",
      "price": "49.99",
      "purchased_at": "2026-08-14T18:00:00Z",
      "expires_at": "2027-08-14T18:00:00Z",
      "is_lifetime": false,
      "is_active": true
    }
  ]
}
```

| Campo | Notas |
|-------|--------|
| `expires_at` | `null` si receta lifetime o sin grant |
| `is_lifetime` | `expires_at` del grant es `null` |
| `is_active` | Grant no revocado y (lifetime o fecha futura) |
