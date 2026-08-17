# Admin — Ajustes del sitio y Firebase Storage

`GET/PATCH /api/v1/admin/site/settings/`  
Auth: JWT staff.

Configura textos de home, redes, teléfonos y **dónde se guardan las imágenes**.

Guía paso a paso (consola + PATCH): [configurar-integraciones.md](../../../configurar-integraciones.md).

Video (Bunny.net): [bunny.md](./bunny.md) — `GET/PATCH /site/bunny/`.  
Pagos (Stripe): [stripe.md](./stripe.md) — `GET/PATCH /site/stripe/`.  
Mailchimp: [mailchimp.md](./mailchimp.md) — `GET/PATCH /site/mailchimp/`.  
Google OAuth: [google.md](./google.md) — `GET/PATCH /site/google/`.

## Prioridad de storage

1. **Firebase Storage** si `firebase_enabled=true` y hay credenciales válidas (configurado aquí).
2. **Digital Ocean Spaces** si existen vars `AWS_*` en el servidor.
3. **Filesystem local** (`MEDIA_ROOT`) en desarrollo.

Todas las `ImageField` (portadas de cursos/recetas, sliders, botones) y los `FileField` de recursos de curso usan este storage. Los recursos (`courses/resources/…`) **no** se hacen públicos en Firebase: se sirven solo vía API con compra.

## GET — no expone el JSON privado

`firebase_credentials_json` es **write-only**. La lectura devuelve `firebase_configured: true/false` y `storage_backend`: `firebase` \| `s3` \| `local`.

## PATCH — ejemplo de contenido

Redes y teléfonos son globales. **Sobre mí** va en `translations` por idioma.

```json
{
  "social_instagram": "https://instagram.com/petralicious",
  "phone_1": "+421 111 222",
  "contact_email": "hola@petralicious.sk",
  "translations": [
    {
      "language_code": "es",
      "about_title": "Sobre mí",
      "about_html": "<p>Chef y docente…</p>"
    },
    {
      "language_code": "en",
      "about_title": "About me",
      "about_html": "<p>Chef and teacher…</p>"
    }
  ]
}
```

En GET, `translations` lista `language_code`, `about_title`, `about_html`.
Si omites `translations` en un PATCH, se conservan las traducciones existentes.

## PATCH — activar Firebase

Desde Firebase Console → Project settings → Service accounts → **Generate new private key**.  
Bucket: normalmente `TU_PROJECT.appspot.com`.

```json
{
  "firebase_enabled": true,
  "firebase_project_id": "tu-proyecto",
  "firebase_bucket": "tu-proyecto.appspot.com",
  "firebase_credentials_json": "{ ... JSON completo del service account ... }"
}
```

Si omites `firebase_credentials_json` en un PATCH posterior, se conservan las credenciales ya guardadas.

### Reglas de Storage (lectura pública)

El Admin SDK escribe saltándose las rules. El frontend necesita lectura pública:

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

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 422 | `FIREBASE_CONFIG_INCOMPLETE` | Enabled sin project/bucket/JSON |
| 422 | `FIREBASE_CREDENTIALS_INVALID` | JSON inválido o no es service account |
