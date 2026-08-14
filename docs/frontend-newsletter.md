# Frontend — Newsletter + Mailchimp

El frontend **no** habla con Mailchimp. La API key queda en el servidor.

Alta: `POST /api/v1/public/newsletter/` (sin JWT).  
Detalle del contrato: [apis/public/newsletter.md](./apis/public/newsletter.md).  
Keys en admin: [configurar-integraciones.md](./configurar-integraciones.md) §4.

## Qué hace cada lado

| | Frontend | Backend |
|---|----------|---------|
| Idioma | Lo conoce por la web activa (ruta, locale, dominio). **No** pidas idioma en el form. Envía `language: "es"` o `"sk"`. | Group **Idioma / Jazyk** = Español o Slovenčina + tag `WEB_ES` / `WEB_SK` |
| Nombre, email | Inputs del form | Audience Petralicious (`60e8a3969d`) |
| Consentimiento | Checkbox obligatorio + enlace a Política de privacidad | Rechaza si `consent` no es `true` (`CONSENT_REQUIRED`) |
| Tags extra | Opcional: `FREEBIE_ES`, `WAITLIST`, … | Se añaden **además** de `WEB_ES`/`WEB_SK` |

## Formulario

Campos visibles:

1. Nombre
2. Email
3. Checkbox obligatorio: recibir comunicaciones comerciales / newsletter, con enlace a la Política de privacidad

No muestres selector de idioma. No envíes la API key.

### Web ES

```http
POST /api/v1/public/newsletter/
Content-Type: application/json
```

```json
{
  "name": "Ana Pérez",
  "email": "ana@example.com",
  "language": "es",
  "consent": true
}
```

### Web SK

```json
{
  "name": "Ana Nováková",
  "email": "ana@example.com",
  "language": "sk",
  "consent": true
}
```

`language` solo `"es"` o `"sk"` (minúsculas).

## Tags futuros (freebie, waitlist, …)

Mismo endpoint, mismo form. Añade `tags` según el origen de la página:

```json
{
  "name": "Ana Pérez",
  "email": "ana@example.com",
  "language": "es",
  "consent": true,
  "tags": ["FREEBIE_ES"]
}
```

Reglas: `A-Z`, números y `_`, máximo 10, ejemplo `WAITLIST`, `FREEBIE_SK`.  
No hace falta mandar `WEB_ES` / `WEB_SK`: el backend los pone solo.

## Respuestas

| HTTP | code | UI |
|------|------|-----|
| 201 | — | Éxito (el contacto queda en cola hacia Mailchimp) |
| 409 | `EMAIL_ALREADY_SUBSCRIBED` | Ya estaba suscrito |
| 422 | `CONSENT_REQUIRED` | Checkbox sin marcar |
| 422 | `NEWSLETTER_LANGUAGE_INVALID` | `language` distinto de `es`/`sk` |
| 422 | `NEWSLETTER_NAME_REQUIRED` | Nombre vacío |
| 422 | `NEWSLETTER_TAG_INVALID` | Tag mal formado |

Éxito:

```json
{
  "data": { "message": "Suscripción registrada." },
  "meta": {}
}
```

No esperes a Mailchimp en el cliente: si Marketing no está configurado, el alta igual se guarda y el admin ve `mailchimp_status: skipped`.

## Privacidad

El texto del checkbox y la URL de la política son copy del frontend (por idioma). El backend solo exige `consent: true`.
