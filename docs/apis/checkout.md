# POST /api/v1/checkout/create-session/

JWT `type=user`. Crea una **Stripe Checkout Session** (pago único) con el carrito actual.

Guía de Dashboard: [admin/site/stripe.md](./admin/site/stripe.md).

```json
{ "lang": "es" }
```

`lang` es opcional (nombres en Checkout y locale).

## Response 200

```json
{
  "data": {
    "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_...",
    "session_id": "cs_test_...",
    "order_id": "uuid",
    "total": "49.99",
    "currency": "eur"
  },
  "meta": {}
}
```

El frontend redirige a `checkout_url`. Apple Pay y Google Pay salen en esa página si están activos en Stripe Dashboard.

El acceso al contenido **no** se otorga aquí: espera el webhook `checkout.session.completed`.
