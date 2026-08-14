# POST /api/v1/public/newsletter/

Alta al newsletter. Sin autenticación. Mailchimp lo hace el **servidor** (la API key no va al frontend).

Guía frontend (idioma, consentimiento, tags): [frontend-newsletter.md](../../frontend-newsletter.md).

## Request

```json
{
  "name": "Ana Pérez",
  "email": "ana@example.com",
  "language": "es",
  "consent": true,
  "tags": ["FREEBIE_ES"]
}
```

| Campo | Obligatorio | Notas |
|-------|-------------|--------|
| `name` | Sí | Nombre para merge `FNAME` / `LNAME` |
| `email` | Sí | |
| `language` | Sí | `"es"` (web ES) o `"sk"` (web SK). Lo decide el frontend, no el usuario |
| `consent` | Sí | Debe ser `true` (comunicaciones comerciales + privacidad) |
| `tags` | No | Extra: `FREEBIE_ES`, `WAITLIST`, … Máx. 10. No hace falta `WEB_ES`/`WEB_SK` |

## Response 201

```json
{
  "data": { "message": "Suscripción registrada." },
  "meta": {}
}
```

El backend guarda el contacto y, si Mailchimp Marketing está activo, lo envía a la Audience **Petralicious** con:

- Group **Idioma / Jazyk** = Español o Slovenčina
- Tags `WEB_ES` o `WEB_SK` + los `tags` del request

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 409 | `EMAIL_ALREADY_SUBSCRIBED` | Email ya registrado |
| 422 | `CONSENT_REQUIRED` | `consent` no es `true` |
| 422 | `NEWSLETTER_LANGUAGE_INVALID` | `language` distinto de `es`/`sk` |
| 422 | `NEWSLETTER_NAME_REQUIRED` | Nombre vacío |
| 422 | `NEWSLETTER_TAG_INVALID` | Tag con formato inválido |

Listado staff: `GET /api/v1/admin/newsletter/`.
