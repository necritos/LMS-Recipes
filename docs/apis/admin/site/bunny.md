# Admin — Bunny.net Stream

`GET/PATCH /api/v1/admin/site/bunny/`  
Auth: JWT staff.

Credenciales de video **desde el admin**, igual que Firebase: nada de API keys en `.env`.

Guía paso a paso (dashboard + PATCH): [configurar-integraciones.md](../../../configurar-integraciones.md).

## GET — no expone secretos

`bunny_api_key` y `bunny_token_key` son **write-only**. La lectura devuelve:

| Campo | Descripción |
|-------|-------------|
| `bunny_enabled` | Si se firman URLs |
| `bunny_library_id` | Library ID de Stream |
| `bunny_cdn_hostname` | Hostname del pull zone (sin `https://`) |
| `bunny_token_ttl_seconds` | TTL del token (60–14400, default 3600) |
| `bunny_configured` | `true` si hay library + token key |
| `bunny_api_configured` | `true` si hay API key de Stream |

## PATCH — activar Bunny

En Bunny Stream → tu library → pestaña **API**: Library ID, CDN hostname y **API Key**.  
La **Token key** no está ahí: menú **Security** de la misma library → Token authentication. Si no hay key aparte, usa la API Key también como `bunny_token_key`.

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

Si omites `bunny_api_key` o `bunny_token_key` (o envías `""`) en un PATCH posterior, se conservan las keys ya guardadas.

`cdn_hostname` es opcional: si existe, `/me/` también devuelve `hls_url`. El player puede usar solo `signed_video_url` (iframe embed).

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 422 | `BUNNY_CONFIG_INCOMPLETE` | Enabled sin library_id o token_key |
| 422 | `BUNNY_TTL_INVALID` | TTL fuera de 60–14400 |
| 503 | `BUNNY_NOT_CONFIGURED` | Usuario pide video y Bunny no está activo |
