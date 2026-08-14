# Configurar Firebase, Bunny.net, Stripe, Mailchimp y Google OAuth

Las integraciones se activan **desde el admin** (JWT staff). Nada de keys en `.env` (salvo fallback legacy de Google).

1. Login staff: `POST /api/v1/admin/auth/login/` → `access`
2. `Authorization: Bearer <access>`
3. `PATCH` al endpoint de cada servicio
4. `GET` para comprobar: `*_configured: true` (los secretos **no** se devuelven)

Detalle por API: [Firebase](./apis/admin/site/settings.md) · [Bunny](./apis/admin/site/bunny.md) · [Stripe](./apis/admin/site/stripe.md) · [Mailchimp](./apis/admin/site/mailchimp.md) · [Google OAuth](./apis/admin/site/google.md)

Formulario newsletter (frontend): [frontend-newsletter.md](./frontend-newsletter.md)

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

## 4. Mailchimp (newsletter + emails transaccionales)

Dos productos en la misma cuenta:

| Uso | Producto Mailchimp | Campo admin |
|-----|--------------------|-------------|
| Newsletter (Audience, groups, tags) | **Marketing API** | `mailchimp_api_key` |
| Bienvenida, recuperación de contraseña, confirmación de compra | **Transactional** (Mandrill) | `mailchimp_transactional_api_key` |

La API key **nunca** va al frontend. El formulario público llama a `POST /api/v1/public/newsletter/` y el servidor habla con Mailchimp.

Audience del cliente (valores a pegar):

| Campo | Valor |
|-------|--------|
| Audience | Petralicious |
| Audience ID | `60e8a3969d` |
| Group (Interest Category) | Idioma / Jazyk |
| Interests | Español · Slovenčina |
| Tags automáticos | `WEB_ES` (web ES) · `WEB_SK` (web SK) |

### 4.1 Marketing API (newsletter)

1. Entra en [Mailchimp](https://admin.mailchimp.com) → icono de perfil → **Account & billing** → **Extras → API keys** → **Create A Key**. Copia la key (termina en `-us21` o similar: ese sufijo es el datacenter).
2. **Audience → Petralicious → Settings → Audience name and defaults**. Copia el **Audience ID** (`60e8a3969d`).
3. En la misma Audience: **Manage contacts → Groups**. Confirma el group **Idioma / Jazyk** con **Español** y **Slovenčina**. No hace falta que el usuario elija idioma: lo envía el frontend según la web (`es` / `sk`).
4. (Opcional, GDPR) Si la Audience tiene Marketing Permissions, copia los IDs (o déjalos vacíos: el backend intenta leerlos de un contacto existente).

Guarda Marketing **antes** de pedir los IDs de grupo:

```http
PATCH /api/v1/admin/site/mailchimp/
Authorization: Bearer <staff>
```

```json
{
  "mailchimp_enabled": true,
  "mailchimp_api_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-us21",
  "mailchimp_audience_id": "60e8a3969d",
  "mailchimp_audience_name": "Petralicious",
  "mailchimp_web_tag_es": "WEB_ES",
  "mailchimp_web_tag_sk": "WEB_SK",
  "mailchimp_double_opt_in": false,
  "mailchimp_from_email": "hola@petralicious.sk",
  "mailchimp_from_name": "Petralicious"
}
```

`double_opt_in: false` porque el formulario ya exige consentimiento + enlace a privacidad. Si en Mailchimp la Audience tiene double opt-in obligatorio, pon `true` (Mailchimp mandará el correo de confirmación).

Luego lista grupos e interests:

```http
GET /api/v1/admin/site/mailchimp/interests/
Authorization: Bearer <staff>
```

Copia el `id` de **Idioma / Jazyk** y los de **Español** / **Slovenčina**:

```http
PATCH /api/v1/admin/site/mailchimp/
Authorization: Bearer <staff>
```

```json
{
  "mailchimp_language_category_id": "xxxxxxxxxx",
  "mailchimp_interest_es_id": "yyyyyyyyyy",
  "mailchimp_interest_sk_id": "zzzzzzzzzz"
}
```

Si dejas esos IDs vacíos, el backend los resuelve por nombre (`Idioma / Jazyk`, `Español`, `Slovenčina`) en cada alta. Pegarlos evita una llamada extra y es más estable.

Tags futuros (`FREEBIE_ES`, `FREEBIE_SK`, `WAITLIST`, …): el frontend los manda en `tags` y el servidor los añade **además** de `WEB_ES` / `WEB_SK`. No hace falta reconfigurar admin.

### 4.2 Transactional / Mandrill (correos transaccionales)

Hace falta para códigos únicos de recuperación de contraseña (un journey de Marketing no sirve).

1. En Mailchimp: **App → Transactional Email** (o [mandrillapp.com](https://mandrillapp.com) con la misma cuenta).
2. **Settings → SMTP & API Info → New API Key**. Esa key es **distinta** de la Marketing.
3. **Sending Domains**: verifica `petralicious.sk` (DKIM/SPF). El `mailchimp_from_email` debe ser de ese dominio.
4. Pega en admin:

```http
PATCH /api/v1/admin/site/mailchimp/
Authorization: Bearer <staff>
```

```json
{
  "mailchimp_transactional_api_key": "md-xxxxxxxx",
  "mailchimp_from_email": "hola@petralicious.sk",
  "mailchimp_from_name": "Petralicious"
}
```

Con eso salen por Mandrill:

- Bienvenida al registrarse
- Recuperación de contraseña (código OTP)
- Confirmación de compra (tras webhook Stripe)

`GET /admin/site/mailchimp/`: `mailchimp_configured` y `mailchimp_transactional_configured`. Las keys no se leen. Si envías `""` en un PATCH posterior, se conservan.

Sin Mandrill, el fallback es SMTP de `.env` (`EMAIL_HOST`, …) o consola en local.

---

## 5. Google OAuth (login / registro con Google)

El flujo de esta plataforma es:

1. El **frontend** muestra el botón de Google (Google Identity Services / Sign-In).
2. Google devuelve un **`id_token`** (JWT) al navegador.
3. El frontend llama `POST /api/v1/auth/google/` con ese `id_token`.
4. El **backend** verifica el token con el **Client ID** (audience) y crea/vincula el usuario.

Por eso el Client ID tiene que ser el **mismo** en:
- Google Cloud Console (OAuth client tipo **Web application**)
- Admin del backend (`PATCH /admin/site/google/`)
- Frontend (GIS), o el frontend lo lee de `GET /api/v1/public/google-oauth/`

El **Client Secret** no se usa para verificar `id_token`. Se puede guardar en admin por si más adelante usáis otro flujo; para Sign-In con Google **basta el Client ID**.

### 5.1 Crear el OAuth Client en Google Cloud Console

Haz estos pasos **en orden**:

#### A) Proyecto

1. Entra en [Google Cloud Console](https://console.cloud.google.com/).
2. Arriba a la izquierda, selector de proyecto → **New Project**.
3. Nombre sugerido: `Petralicious` (o el mismo proyecto de Firebase si ya lo usáis para Storage).
4. **Create** y selecciona ese proyecto.

> Si ya usas Firebase Storage en el mismo producto, puedes abrir el proyecto de Firebase desde Cloud Console (mismo Project ID). No hace falta un proyecto aparte.

#### B) Pantalla de consentimiento OAuth (obligatoria la primera vez)

1. Menú ☰ → **APIs & Services** → **OAuth consent screen**.
2. Tipo de usuario:
   - **External** (usuarios con cualquier Gmail / Google Account) → lo habitual en producción.
   - **Internal** solo si es Google Workspace de tu organización.
3. **Create**.
4. Rellena:
   - **App name:** `Petralicious` (o el nombre que vea el usuario en el popup de Google).
   - **User support email:** tu email.
   - **App logo** (opcional).
   - **Application home page:** `https://petralicious.sk` (o el dominio principal del frontend).
   - **Authorized domains:** añade `petralicious.sk`, `petralicious.com` y, si usáis Firebase Hosting, `web.app` / `firebaseapp.com` cuando Google lo pida.
   - **Developer contact:** tu email.
5. **Save and Continue**.
6. **Scopes:** no hace falta scopes raros. Con los defaults (`openid`, `email`, `profile`) basta para login. **Save and Continue**.
7. **Test users** (si la app está en modo *Testing*): añade los Gmail con los que vas a probar. En producción publica la app (**Publishing status → In production**) cuando esté lista; si no, solo los test users podrán entrar.
8. **Save and Continue** → **Back to Dashboard**.

#### C) Crear credenciales (Client ID Web)

1. Menú ☰ → **APIs & Services** → **Credentials**.
2. **+ Create Credentials** → **OAuth client ID**.
3. Application type: **Web application** (importante: no uses “Android”, “iOS” ni “Desktop” para este flujo).
4. Name: `Petralicious Web` (solo etiqueta interna).
5. **Authorized JavaScript origins** — orígenes desde los que el frontend carga el botón de Google. **Sin path**, solo esquema + host (+ puerto en local):

| Origen | Cuándo |
|--------|--------|
| `http://localhost:5173` | Frontend Vite en local (ajusta el puerto si es otro) |
| `http://127.0.0.1:5173` | Igual, por IP |
| `https://petralicious.sk` | Web SK producción |
| `https://www.petralicious.sk` | Si usáis www |
| `https://petralicious.com` | Web ES / .com |
| `https://www.petralicious.com` | Si usáis www |
| `https://petralicious-aac3c.web.app` | Admin / app en Firebase Hosting (pon el ID real de tu proyecto) |
| `https://petralicious-aac3c.firebaseapp.com` | Dominio alternativo de Firebase (si lo usáis) |

Google **no** admite wildcards tipo `*.web.app` aquí: cada hostname hay que añadirlo a mano.

6. **Authorized redirect URIs** — con Google Identity Services (GIS) y `id_token` en el frontend a menudo **no** hace falta redirect. Si GIS o tu librería lo pide, añade por ejemplo:
   - `http://localhost:5173`
   - `https://petralicious.sk`
   - `https://petralicious.com`
   - la URL de tu hosting Firebase  

   No pongas la URL de la API (`https://api…`) salvo que implementéis un flujo server-side con redirect (este backend **no** usa ese flujo).

7. **Create**.
8. Copia:
   - **Client ID** → parece `123456789-xxxxx.apps.googleusercontent.com`
   - **Client secret** → opcional para este backend (write-only en admin)

Deja la ventana abierta o guárdalos en un sitio seguro: el secret solo se muestra bien al crearlo.

### 5.2 Pegar en admin (backend)

```http
PATCH /api/v1/admin/site/google/
Authorization: Bearer <staff>
Content-Type: application/json
```

```json
{
  "google_oauth_enabled": true,
  "google_client_id": "123456789-xxxxxxxxxxxx.apps.googleusercontent.com",
  "google_client_secret": "GOCSPX-xxxxxxxx" 
}
```

| Campo | Obligatorio | Notas |
|-------|-------------|--------|
| `google_oauth_enabled` | Sí para activar | Sin esto el backend ignora el Client ID del admin y solo mira env legacy |
| `google_client_id` | Sí si enabled | Debe terminar en `.apps.googleusercontent.com` |
| `google_client_secret` | No | Write-only; si mandas `""` o lo omites, se conserva el anterior |

Comprobar:

```http
GET /api/v1/admin/site/google/
Authorization: Bearer <staff>
```

```json
{
  "data": {
    "google_oauth_enabled": true,
    "google_client_id": "123456789-xxxxxxxxxxxx.apps.googleusercontent.com",
    "google_configured": true
  },
  "meta": {}
}
```

`google_client_secret` **nunca** vuelve en el GET.  
Errores: `422 GOOGLE_CONFIG_INCOMPLETE` (enabled sin Client ID), `422 GOOGLE_CLIENT_ID_INVALID` (formato incorrecto).

### 5.3 Frontend

1. Usa el **mismo** Client ID.
2. Opción recomendada: leerlo del backend (sin hardcodear):

```http
GET /api/v1/public/google-oauth/
```

```json
{
  "data": {
    "enabled": true,
    "client_id": "123456789-xxxxxxxxxxxx.apps.googleusercontent.com"
  },
  "meta": {}
}
```

Si `enabled: false`, no muestres el botón de Google.

3. Con GIS, inicializa con ese `client_id`, pide el `id_token` / credential JWT y envíalo:

```http
POST /api/v1/auth/google/
Content-Type: application/json
```

```json
{ "id_token": "<credential-jwt-de-google>" }
```

Detalle API: [apis/auth/google.md](./apis/auth/google.md).

### 5.4 Errores típicos

| Síntoma | Causa habitual | Qué hacer |
|---------|----------------|-----------|
| Popup de Google: “origen no autorizado” | Falta el hostname en **Authorized JavaScript origins** | Añade exactamente la URL del navegador (https, sin `/` final) |
| Backend `503 GOOGLE_NOT_CONFIGURED` | Admin sin enabled + Client ID (y sin env) | `PATCH /admin/site/google/` |
| Backend `401 INVALID_GOOGLE_TOKEN` | Client ID del frontend ≠ Client ID del backend, o token caducado | Misma Client ID en ambos; pide token fresco |
| Solo algunos Gmail pueden entrar | Consent screen en **Testing** | Añade test users o publica la app |
| Funciona en local y no en prod (o al revés) | Origen prod no listado en Google Console | Añade `https://petralicious.sk`, `.com`, `.web.app`, etc. |

### 5.5 Legacy `.env`

Si aún tienes `GOOGLE_CLIENT_ID=...` en el Droplet y **no** has activado el admin (`google_oauth_enabled: false`), el backend sigue usando el env.  
Cuando actives admin, **manda el admin**: el env se ignora mientras `google_oauth_enabled` sea `true`. Puedes borrar `GOOGLE_CLIENT_ID` del `.env` después de migrar.

---

## Orden recomendado

1. Firebase → las imágenes del CMS y del catálogo suben ya al bucket.
2. Bunny → videos firmados en `/me/courses/{id}/lessons/` (hace falta un `AccessGrant`; en test se crea en Django admin o pagando).
3. Stripe → carrito + checkout; el webhook crea el grant.
4. Mailchimp Marketing → newsletter. Mailchimp Transactional → bienvenida / reset / compra.
5. Google OAuth → login/registro con Google (Client ID Web + orígenes en Console + `PATCH /admin/site/google/`).

Sin webhook de Stripe el usuario paga y **no ve videos**.  
Sin Marketing API el alta de newsletter se guarda en el admin (`mailchimp_status: skipped`) pero no llega a la Audience.  
Sin Transactional, los correos transaccionales no salen por Mailchimp (solo SMTP/consola).  
Sin Google configurado, `POST /auth/google/` responde `503 GOOGLE_NOT_CONFIGURED`.
