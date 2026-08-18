# Admin — Intentos de pago

Listado de cada intento de Stripe: iniciado, correcto, fallido o sesión expirada.  
Un mismo pedido puede tener varios registros (p. ej. tarjeta rechazada y luego pagada).

**Prefijo:** `/api/v1/admin/payments/`  
**Auth:** JWT `type=staff`

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/payments/` | Listado paginado |
| GET | `/payments/{id}/` | Detalle |

## Query params (listado)

| Param | Descripción |
|-------|-------------|
| `outcome` | `started` \| `succeeded` \| `failed` \| `expired` |
| `search` | Email, nombre, `stripe_session_id` o `payment_intent` |
| `page` | Página |
| `page_size` | Máx. 100 |

## Response 200 (listado)

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "outcome": "succeeded",
      "amount": "49.99",
      "currency": "eur",
      "customer_email": "user@example.com",
      "user": {
        "id": "uuid",
        "email": "user@example.com",
        "first_name": "María",
        "last_name": "García",
        "full_name": "María García"
      },
      "order_id": "uuid",
      "order_status": "paid",
      "items": [
        {
          "title": "Curso de Pasta",
          "unit_price": "49.99",
          "product_type": "course",
          "product_id": "uuid"
        }
      ],
      "stripe_session_id": "cs_test_...",
      "stripe_payment_intent": "pi_...",
      "stripe_event_id": "evt_...",
      "stripe_event_type": "checkout.session.completed",
      "failure_code": "",
      "failure_message": "",
      "created_at": "2026-08-18T16:00:00Z",
      "updated_at": "2026-08-18T16:00:00Z"
    }
  ]
}
```

| `outcome` | Cuándo |
|-----------|--------|
| `started` | El usuario abre Stripe Checkout |
| `succeeded` | Webhook `checkout.session.completed` |
| `failed` | Webhook `payment_intent.payment_failed` (`failure_code` / `failure_message` de Stripe) |
| `expired` | Webhook `checkout.session.expired` |
