# Admin — Sitio (CMS)

JWT `type=staff`. Prefijo `/api/v1/admin/`.

**Cómo obtener keys y pegarlas en admin:** [configurar-integraciones.md](../../../configurar-integraciones.md) (Firebase, Bunny, Stripe, Mailchimp).

| Recurso | Guía | Endpoints |
|---------|------|-----------|
| Ajustes + Firebase Storage | [settings.md](./settings.md) | `GET/PATCH /site/settings/` |
| Bunny.net Stream | [bunny.md](./bunny.md) | `GET/PATCH /site/bunny/` |
| Stripe (pagos) | [stripe.md](./stripe.md) | `GET/PATCH /site/stripe/` |
| Mailchimp | [mailchimp.md](./mailchimp.md) | `GET/PATCH /site/mailchimp/`, `GET /site/mailchimp/interests/` |
| Sliders | [sliders.md](./sliders.md) | `GET/POST /site/sliders/`, `GET/PATCH/DELETE /site/sliders/{id}/` |
| Por dónde empezar | [start-buttons.md](./start-buttons.md) | `/site/start-buttons/` |
| Referencias | [testimonials.md](./testimonials.md) | `/site/testimonials/` |
| Contacto | [contact.md](./contact.md) | `/contact/` |
| Newsletter | [newsletter.md](./newsletter.md) | `/newsletter/` |
