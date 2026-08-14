# Admin — Google OAuth

`GET/PATCH /api/v1/admin/site/google/`  
Auth: JWT staff.

Client ID de Google Sign-In **desde el admin**, igual que Firebase / Bunny / Stripe / Mailchimp.

Guía paso a paso (Google Cloud Console + PATCH): [configurar-integraciones.md](../../../configurar-integraciones.md) §5.

Frontend puede leer el Client ID público: `GET /api/v1/public/google-oauth/`.  
Login: `POST /api/v1/auth/google/` — [auth/google.md](../../auth/google.md).

---

## GET

| Campo | Descripción |
|-------|-------------|
| `google_oauth_enabled` | Si el backend usa el Client ID guardado aquí |
| `google_client_id` | OAuth Client ID (tipo Web). Visible: es público en el frontend |
| `google_configured` | `true` si enabled + hay Client ID |

`google_client_secret` es **write-only** (no se devuelve).

## PATCH

```json
{
  "google_oauth_enabled": true,
  "google_client_id": "123456789-xxxx.apps.googleusercontent.com",
  "google_client_secret": "GOCSPX-…"
}
```

| Error | Cuándo |
|-------|--------|
| `422 GOOGLE_CONFIG_INCOMPLETE` | `enabled` sin Client ID |
| `422 GOOGLE_CLIENT_ID_INVALID` | No termina en `.apps.googleusercontent.com` |

Si omites `google_client_secret` o envías `""`, se conserva el valor anterior.

Con `google_oauth_enabled: true`, el env `GOOGLE_CLIENT_ID` se ignora.
