# Admin — Stripe (pagos)

`GET/PATCH /api/v1/admin/site/stripe/`  
Auth: JWT staff.

Las **claves se guardan aquí**, igual que Firebase y Bunny: no van en `.env`.  
El GET **nunca** devuelve `stripe_secret_key` ni `stripe_webhook_secret`.

Guía corta de las integraciones: [configurar-integraciones.md](../../../configurar-integraciones.md).

---

## Qué activar en Stripe Dashboard

Entra en [https://dashboard.stripe.com](https://dashboard.stripe.com). Usa **Test mode** (interruptor arriba a la derecha) hasta que el cobro real esté listo.

Haz esto **antes** de pegar keys en el admin:

| # | En Stripe | Qué hacer |
|---|-----------|-----------|
| 1 | Cuenta | País y moneda **EUR**. **Settings → Public details**: nombre, soporte, logo (salen en Checkout). |
| 2 | **Developers → API keys** | Copia Secret `sk_test_...` y Publishable `pk_test_...`. |
| 3 | **Settings → Payment methods** | Activa **Cards**, **Apple Pay** y **Google Pay**. Link es opcional. |
| 4 | **Developers → Webhooks → Add endpoint** | URL, eventos y signing secret (abajo). |

No hace falta Billing ni suscripciones: el cobro es **one-time**.

Apple Pay y Google Pay aparecen solos en Checkout hosted (`checkout.stripe.com`). **No** hay que registrar dominio ni subir el archivo de Apple (eso solo aplica si el frontend embebiera Payment Element).

### Webhook (obligatorio)

Sin webhook el usuario paga pero **no recibe AccessGrant** (no ve videos).

| Campo | Valor |
|-------|--------|
| URL (prod) | `https://petralicious.sk/api/v1/webhooks/stripe/` |
| Eventos | `checkout.session.completed` y `payment_intent.payment_failed` (opcional: `checkout.session.expired`) |
| Signing secret | `whsec_...` → campo admin `stripe_webhook_secret` |

En local: `stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe/` y usa el `whsec_` que imprime el CLI.

### De Dashboard → campos del admin

| En Stripe | Campo `PATCH /admin/site/stripe/` |
|-----------|-----------------------------------|
| Secret key `sk_test_...` / `sk_live_...` | `stripe_secret_key` (write-only) |
| Publishable key `pk_test_...` / `pk_live_...` | `stripe_publishable_key` |
| Webhook signing secret `whsec_...` | `stripe_webhook_secret` (write-only) |
| Test mode / Live mode | `stripe_mode`: `test` o `live` (el prefijo de la secret debe coincidir) |
| Moneda de la cuenta | `stripe_currency`: `eur` |
| URLs del frontend (no del Dashboard) | `stripe_success_url`, `stripe_cancel_url` |

**Settings → Checkout:** branding (logo/color). Success/cancel las pone el backend con los campos de arriba, no las del Dashboard.

### Tarjetas de prueba (Test mode)

| Número | Resultado |
|--------|-----------|
| `4242 4242 4242 4242` | Pago OK |
| `4000 0000 0000 9995` | Rechazado |
| Fecha | Cualquier futura |
| CVC | Cualquier 3 dígitos |

---

## PATCH — guardar en admin

Cuando tengas las keys y el `whsec_` del Dashboard:

```http
PATCH /api/v1/admin/site/stripe/
Authorization: Bearer <staff>
```

```json
{
  "stripe_enabled": true,
  "stripe_mode": "test",
  "stripe_secret_key": "sk_test_...",
  "stripe_publishable_key": "pk_test_...",
  "stripe_webhook_secret": "whsec_...",
  "stripe_success_url": "https://petralicious.sk/checkout/success",
  "stripe_cancel_url": "https://petralicious.sk/checkout/cancel",
  "stripe_currency": "eur"
}
```

El backend añade `session_id={CHECKOUT_SESSION_ID}` a `success_url` si no está.  
Si omites las keys o envías `""`, se conservan las ya guardadas.

### GET (sin secretos)

| Campo | Descripción |
|-------|-------------|
| `stripe_enabled` | Si se pueden crear sesiones |
| `stripe_mode` | `test` \| `live` |
| `stripe_publishable_key` | Pública |
| `stripe_success_url` / `stripe_cancel_url` | Redirect del frontend |
| `stripe_currency` | ISO 3 letras (`eur`) |
| `stripe_configured` | Hay secret + success URL + cancel URL |
| `stripe_webhook_configured` | Hay `whsec_` |

---

## Flujo de compra (APIs)

1. Usuario: `POST /api/v1/me/cart/` `{ "course_id" }` o `{ "recipe_id" }`
2. `POST /api/v1/checkout/create-session/` → `{ checkout_url, session_id, order_id }`  
   Opcional: `stripe_success_url` y `stripe_cancel_url` del dominio del frontend (si no, las del admin).
3. Frontend redirige a `checkout_url` (tarjeta / Apple Pay / Google Pay).
4. Stripe llama `POST /api/v1/webhooks/stripe/` → Order pagada + AccessGrant + email.
5. El video sigue exigiendo grant (`GET /me/courses/{id}/lessons/`).

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 422 | `STRIPE_CONFIG_INCOMPLETE` | Enabled sin secret/URLs |
| 422 | `STRIPE_KEY_MODE_MISMATCH` | `sk_test_` en modo live o al revés |
| 422 | `CART_EMPTY` | Checkout sin ítems |
| 503 | `STRIPE_NOT_CONFIGURED` | Checkout con Stripe apagado |
| 503 | `STRIPE_WEBHOOK_NOT_CONFIGURED` | Webhook sin `whsec_` |
| 400 | `STRIPE_SIGNATURE_INVALID` | Webhook sin firma válida |
