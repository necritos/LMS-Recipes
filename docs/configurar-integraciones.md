# Configurar Firebase, Bunny.net y Stripe

Las tres integraciones se activan **desde el admin** (JWT staff). Nada de keys en `.env`.

1. Login staff: `POST /api/v1/admin/auth/login/` → `access`
2. `Authorization: Bearer <access>`
3. `PATCH` al endpoint de cada servicio
4. `GET` para comprobar: `*_configured: true` (los secretos **no** se devuelven)

Detalle por API: [Firebase](./apis/admin/site/settings.md) · [Bunny](./apis/admin/site/bunny.md) · [Stripe](./apis/admin/site/stripe.md)

---

## 0. Login admin

```http
POST /api/v1/admin/auth/login/
```

```json
{ "email": "admin@petralicious.sk", "password": "..." }
```

Usa el `access` en todos los `PATCH` de abajo.

---

## 1. Firebase Storage (imágenes)

Sirve para portadas de cursos/recetas, sliders y botones de home.

### En Google Cloud / Firebase Console

1. Entra en [Firebase Console](https://console.firebase.google.com) → crea o abre el proyecto.
2. **Build → Storage → Get started** (modo producción). Elige una ubicación y crea el bucket.
3. Anota el **bucket**: suele ser `tu-proyecto.appspot.com` (o `tu-proyecto.firebasestorage.app`).
4. **Project settings** (engranaje) → **Service accounts** → **Generate new private key**.  
   Se descarga un JSON (`type: "service_account"`).
5. **Storage → Rules** → publica reglas de **lectura pública** (el backend escribe con el Admin SDK; el frontend solo lee URLs):

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read: if true;
      allow write: if false;
    }
  }
}
```

### Pegar en admin

```http
PATCH /api/v1/admin/site/settings/
Authorization: Bearer <staff>
```

```json
{
  "firebase_enabled": true,
  "firebase_project_id": "tu-proyecto",
  "firebase_bucket": "tu-proyecto.appspot.com",
  "firebase_credentials_json": "{ ... pega aquí el JSON entero del service account ... }"
}
```

`GET` del mismo endpoint: `firebase_configured: true`, `storage_backend: "firebase"`.  
`firebase_credentials_json` es write-only. Si en un PATCH posterior envías `""` o lo omites, se conserva el JSON ya guardado.

Prioridad de storage: Firebase → DO Spaces (`AWS_*` en el servidor) → disco local.

---

## 2. Bunny.net Stream (videos)

Los videos **no** se suben por esta API: se suben en Bunny y aquí solo se guarda el `bunny_video_id` de cada lección/receta.

### En Bunny dashboard

1. Cuenta en [bunny.net](https://bunny.net) → **Stream**.
2. **Add Video Library** (o usa una existente). Copia el **Library ID** (número).
3. Entra en la library. Hay **dos keys distintas**:
   - Pestaña **API** (la que ves ahora): copia **Video Library ID**, **CDN Hostname** (`vz-….b-cdn.net`) y **API Key** (la de lectura/escritura, no la read-only). Eso es `bunny_api_key`. El campo Webhook de esa pantalla se deja vacío.
   - **Token key** (firmas de video): no está en API. En el menú izquierdo de la **misma library** entra en **Security**. Activa **Token authentication** (embed / “Embed view token authentication”) y copia la key.  
     Si Security no muestra una key aparte, usa la **API Key** también como `bunny_token_key` (Bunny firma el iframe con esa clave).  
     Para HLS (`hls_url`): en la pestaña API, **CDN zone management → Manage** (botón naranja) → **Security → Token Authentication** → Enable y copia esa key de la pull zone.
4. Sube los MP4 a la library. En cada video, copia el **Video ID** (UUID).
5. En admin de catálogo, pega ese ID:
   - Lección: `POST/PATCH /api/v1/admin/modules/{id}/lessons/` campo `bunny_video_id`
   - Receta: `PATCH /api/v1/admin/recipes/{slug}/` campo `bunny_video_id`

### Pegar credenciales en admin

```http
PATCH /api/v1/admin/site/bunny/
Authorization: Bearer <staff>
```

```json
{
  "bunny_enabled": true,
  "bunny_library_id": "123456",
  "bunny_cdn_hostname": "vz-xxxxx.b-cdn.net",
  "bunny_api_key": "stream-api-key",
  "bunny_token_key": "token-authentication-key",
  "bunny_token_ttl_seconds": 3600
}
```

`GET`: `bunny_configured: true` (library + token). `bunny_api_key` y `bunny_token_key` no se leen.  
TTL: 60–14400 segundos (default 3600). El player usa `signed_video_url` (iframe embed); nunca se expone el `bunny_video_id` al usuario final.

---

## 3. Stripe (pagos)

Checkout hosted (tarjeta, Apple Pay, Google Pay). El acceso al contenido **solo** se otorga cuando llega el webhook.

### En Stripe Dashboard

Entra en [dashboard.stripe.com](https://dashboard.stripe.com). Deja **Test mode** ON hasta cobrar de verdad.

| # | Dónde | Qué hacer |
|---|--------|-----------|
| 1 | Cuenta | País y moneda **EUR**. **Settings → Public details**: nombre, soporte, logo. |
| 2 | **Developers → API keys** | Secret `sk_test_...` y Publishable `pk_test_...`. |
| 3 | **Settings → Payment methods** | Activa **Cards**, **Apple Pay**, **Google Pay**. Link opcional. |
| 4 | **Developers → Webhooks → Add endpoint** | Ver tabla de abajo. |

No actives Billing ni suscripciones: el cobro es one-time.

Apple Pay / Google Pay salen solos en `checkout.stripe.com`. No hay que registrar dominio ni archivo de Apple.

**Webhook (obligatorio):**

| Campo | Valor |
|-------|--------|
| URL prod | `https://petralicious.sk/api/v1/webhooks/stripe/` |
| Eventos | `checkout.session.completed` y `payment_intent.payment_failed` (opcional: `checkout.session.expired`) |
| Signing secret | `whsec_...` |

Local: `stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe/` y usa el `whsec_` que imprime el CLI.

**Settings → Checkout:** logo y color. Las URLs de success/cancel las pone el backend (campos de abajo), no el Dashboard.

Tarjeta de prueba: `4242 4242 4242 4242` (fecha futura, CVC cualquiera). Rechazo: `4000 0000 0000 9995`.

### Pegar en admin

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

| En Stripe | Campo admin |
|-----------|-------------|
| `sk_test_` / `sk_live_` | `stripe_secret_key` |
| `pk_test_` / `pk_live_` | `stripe_publishable_key` |
| `whsec_` | `stripe_webhook_secret` |
| Test / Live | `stripe_mode` (debe coincidir con el prefijo de la secret) |
| URLs del frontend | `stripe_success_url`, `stripe_cancel_url` |

`GET`: `stripe_configured` y `stripe_webhook_configured`. Secret y `whsec_` no se devuelven.  
En live: mismas pantallas con Test mode OFF → `sk_live_` / `pk_live_` y `stripe_mode: "live"`. El webhook de live es **otro** endpoint/secret.

---

## Orden recomendado

1. Firebase → las imágenes del CMS y del catálogo suben ya al bucket.
2. Bunny → videos firmados en `/me/courses/{id}/lessons/` (hace falta un `AccessGrant`; en test se crea en Django admin o pagando).
3. Stripe → carrito + checkout; el webhook crea el grant.

Sin webhook de Stripe el usuario paga y **no ve videos**.
