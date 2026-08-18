# POST /api/v1/webhooks/stripe/

Sin JWT. Stripe firma el body (`Stripe-Signature`). El signing secret se configura en admin (`PATCH /admin/site/stripe/`).

## Eventos que procesamos

| Evento | Efecto |
|--------|--------|
| `checkout.session.completed` | Order `paid`, Purchase, AccessGrant, vacía carrito, email, intento `succeeded` |
| `payment_intent.payment_failed` | Order `failed`, intento `failed` (código y mensaje de Stripe) |
| `checkout.session.expired` | Order `canceled`, intento `expired` |

Cada intento queda en `PaymentAttempt` (append-only). El admin los lista en [admin/payments.md](../admin/payments.md).

El mismo `event.id` se ignora (idempotencia, HTTP 200 `duplicate`).

## Acceso otorgado

- Curso: `expires_at = now + course.access_days` (default 365).
- Receta lifetime: `expires_at = null`.
- Receta temporal: `now + recipe.access_days`.

## Errores

| HTTP | code |
|------|------|
| 503 | `STRIPE_WEBHOOK_NOT_CONFIGURED` |
| 400 | `STRIPE_SIGNATURE_INVALID` |
| 400 | `STRIPE_PAYLOAD_INVALID` |

Detalle de Dashboard: [admin/site/stripe.md](../admin/site/stripe.md).
