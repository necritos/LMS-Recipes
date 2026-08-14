# Admin — Dashboard y analytics

JWT `type=staff`. Prefijo `/api/v1/admin/`.

Solo órdenes **pagadas** (`status=paid` y `paid_at` no nulo). Importes en string decimal (EUR).

## GET `/admin/dashboard/`

Resumen + ventas recientes + productos más vendidos.

| Query | Default | Descripción |
|-------|---------|-------------|
| `period` | `month` | `day` (hoy), `week` (7 días), `month` (mes calendario), `all` |
| `recent_limit` | `10` | 1–50 |
| `top_limit` | `5` | 1–20 |

`revenue_period` / `orders_paid_period` / `top_products` usan `period`.  
`revenue_all_time` y `recent_orders` son globales.

```json
{
  "data": {
    "currency": "eur",
    "period": {
      "key": "month",
      "from": "2026-08-01T00:00:00-05:00",
      "to": "2026-08-14T19:00:00+00:00"
    },
    "totals": {
      "revenue_all_time": "199.96",
      "revenue_period": "49.99",
      "orders_paid_all_time": 4,
      "orders_paid_period": 1,
      "orders_pending": 2,
      "customers_with_purchases": 3
    },
    "recent_orders": [
      {
        "id": "uuid",
        "total": "49.99",
        "currency": "eur",
        "paid_at": "2026-08-14T18:00:00Z",
        "customer_email": "user@example.com",
        "user_id": "uuid",
        "items": [
          {
            "title": "Curso de Pasta",
            "unit_price": "49.99",
            "product_type": "course",
            "product_id": "uuid"
          }
        ]
      }
    ],
    "top_products": [
      {
        "product_type": "course",
        "product_id": "uuid",
        "slug": "curso-pasta",
        "title": "Curso de Pasta",
        "units": 3,
        "revenue": "149.97"
      }
    ]
  },
  "meta": {}
}
```

## GET `/admin/dashboard/revenue/`

Serie temporal para gráficos.

| Query | Default | Descripción |
|-------|---------|-------------|
| `granularity` | `day` | `day` \| `week` \| `month` |
| `days` | 30 (si `day`) | Ventana hacia atrás (1–366) |

```json
{
  "data": {
    "currency": "eur",
    "granularity": "day",
    "from": "...",
    "to": "...",
    "points": [
      { "date": "2026-08-14", "revenue": "49.99", "orders": 1 }
    ]
  },
  "meta": {}
}
```

Solo aparecen buckets con ventas.

## Errores

| HTTP | code |
|------|------|
| 401 | Token no staff |
| 422 | `PERIOD_INVALID` / `GRANULARITY_INVALID` / `QUERY_INVALID` |
