# Admin — Newsletter

Emails de `POST /api/v1/public/newsletter/`. Mailchimp: [mailchimp.md](./mailchimp.md).

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/newsletter/` | Listado paginado. `?search=` email o nombre. `?mailchimp_status=` `pending\|synced\|failed\|skipped` |
| GET | `/newsletter/{id}/` | Detalle |
| POST | `/newsletter/{id}/resync/` | Reintenta el envío a Mailchimp |
| DELETE | `/newsletter/{id}/` | Baja local y `unsubscribed` en Mailchimp si hay sync |

Cada fila incluye si se envió a Mailchimp y a dónde:

| Campo | Significado |
|-------|-------------|
| `mailchimp_synced` | `true` si `mailchimp_status == synced` |
| `mailchimp_status` | `pending`, `synced`, `failed`, `skipped` (Marketing no configurado) |
| `mailchimp_audience_id` / `mailchimp_audience_name` | Audience (Petralicious / `60e8a3969d`) |
| `mailchimp_group` | Interest: `Español` o `Slovenčina` |
| `mailchimp_tags` | Tags realmente enviados (`WEB_ES`, `FREEBIE_ES`, …) |
| `mailchimp_destination` | Texto listo para UI: `Petralicious (60e8a3969d) · Idioma: Español · tags: WEB_ES` |
| `mailchimp_error` | Detalle si `failed` |
| `tags` | Tags extra que mandó el frontend (sin el WEB_*) |
| `language` | `es` o `sk` |
| `consent` / `consented_at` | Consentimiento comercial |

No hay envío masivo de campañas desde esta API: las campañas se arman en Mailchimp sobre la misma Audience.
