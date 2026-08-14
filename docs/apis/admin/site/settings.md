# Admin — Ajustes del sitio y Firebase Storage

`GET/PATCH /api/v1/admin/site/settings/`  
Auth: JWT staff.

Configura textos de home, redes, teléfonos y **dónde se guardan las imágenes**.

## Prioridad de storage

1. **Firebase Storage** si `firebase_enabled=true` y hay credenciales válidas (configurado aquí).
2. **Digital Ocean Spaces** si existen vars `AWS_*` en el servidor.
3. **Filesystem local** (`MEDIA_ROOT`) en desarrollo.

Todas las `ImageField` (portadas de cursos/recetas, sliders, botones) usan este storage.

## GET — no expone el JSON privado

`firebase_credentials_json` es **write-only**. La lectura devuelve `firebase_configured: true/false` y `storage_backend`: `firebase` \| `s3` \| `local`.

## PATCH — ejemplo de contenido

```json
{
  "about_title": "Sobre mí",
  "about_html": "<p>Chef y docente…</p>",
  "social_instagram": "https://instagram.com/petralicious",
  "social_tiktok": "",
  "social_facebook": "",
  "social_pinterest": "",
  "phone_1": "+421 111 222",
  "phone_2": "",
  "contact_email": "hola@petralicious.sk"
}
```

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
