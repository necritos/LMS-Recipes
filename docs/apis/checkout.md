# POST /api/v1/checkout/create-session/

JWT `type=user`. Crea una **Stripe Checkout Session** (pago único) con el carrito actual.

Guía de Dashboard: [admin/site/stripe.md](./admin/site/stripe.md).

```json
{
  "lang": "es",
  "stripe_success_url": "https://petralicious.com/checkout/success",
  "stripe_cancel_url": "https://petralicious.com/checkout/cancel"
}
```

`lang` es opcional (nombres en Checkout y locale).

`stripe_success_url` y `stripe_cancel_url` son opcionales. Si los envías, Stripe vuelve a **ese** dominio (p. ej. `.com` vs `.sk`) en lugar de las URLs del admin. Si los omites, se usan `stripe_success_url` / `stripe_cancel_url` de `PATCH /admin/site/stripe/`.

Solo se aceptan orígenes permitidos: `petralicious.com`, `petralicious.sk` (y subdominios / `*.web.app`), CORS del servidor, o el host de las URLs del admin. Un dominio ajeno responde `422 CHECKOUT_REDIRECT_NOT_ALLOWED`.

El backend añade `session_id={CHECKOUT_SESSION_ID}` al success si no viene.

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

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 422 | `CART_EMPTY` | Sin ítems |
| 422 | `CHECKOUT_REDIRECT_NOT_ALLOWED` | `stripe_success_url` / `stripe_cancel_url` de un dominio no permitido |
| 503 | `STRIPE_NOT_CONFIGURED` | Stripe apagado o incompleto en admin |
