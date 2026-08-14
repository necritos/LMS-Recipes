# Admin — Mailchimp

`GET/PATCH /api/v1/admin/site/mailchimp/`  
`GET /api/v1/admin/site/mailchimp/interests/`  
Auth: JWT staff.

Credenciales **desde el admin**, igual que Firebase, Bunny y Stripe: nada de API keys en `.env` ni en el frontend.

Guía (dashboard + PATCH): [configurar-integraciones.md](../../../configurar-integraciones.md) §4.  
Formulario público (frontend): [frontend-newsletter.md](../../../frontend-newsletter.md).

---

## GET — no expone secretos

`mailchimp_api_key` y `mailchimp_transactional_api_key` son **write-only**.

| Campo | Descripción |
|-------|-------------|
| `mailchimp_enabled` | Si se sincroniza el newsletter a la Audience |
| `mailchimp_audience_id` | Audience ID (Petralicious: `60e8a3969d`) |
| `mailchimp_audience_name` | Nombre visible en el listado de suscriptores |
| `mailchimp_language_category_id` | Interest category «Idioma / Jazyk» |
| `mailchimp_interest_es_id` / `mailchimp_interest_sk_id` | Interests Español / Slovenčina |
| `mailchimp_web_tag_es` / `mailchimp_web_tag_sk` | Tags automáticos (`WEB_ES`, `WEB_SK`) |
| `mailchimp_double_opt_in` | `pending` en Mailchimp si `true` |
| `mailchimp_marketing_permission_ids` | IDs GDPR (coma); opcional |
| `mailchimp_from_email` / `mailchimp_from_name` | Remitente transaccional |
| `mailchimp_configured` | API key Marketing + Audience ID |
| `mailchimp_transactional_configured` | Hay key Mandrill |
| `mailchimp_server_prefix` | Datacenter leído de la key (`us21`, …) |

Si omites una key (o envías `""`) en un PATCH posterior, se conserva la ya guardada.

## PATCH — ejemplo

```json
{
  "mailchimp_enabled": true,
  "mailchimp_api_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-us21",
  "mailchimp_audience_id": "60e8a3969d",
  "mailchimp_audience_name": "Petralicious",
  "mailchimp_interest_es_id": "…",
  "mailchimp_interest_sk_id": "…",
  "mailchimp_transactional_api_key": "md-…",
  "mailchimp_from_email": "hola@petralicious.sk",
  "mailchimp_from_name": "Petralicious"
}
```

`422 MAILCHIMP_CONFIG_INCOMPLETE` si `mailchimp_enabled` y faltan API key o Audience ID.  
`422 MAILCHIMP_API_KEY_INVALID` si la Marketing key no termina en datacenter (`-us21`).

## Interests (IDs del group)

Tras guardar la Marketing key:

```http
GET /api/v1/admin/site/mailchimp/interests/
```

```json
{
  "data": {
    "categories": [
      {
        "id": "abc",
        "title": "Idioma / Jazyk",
        "type": "hidden",
        "interests": [
          { "id": "esid", "name": "Español" },
          { "id": "skid", "name": "Slovenčina" }
        ]
      }
    ]
  },
  "meta": {}
}
```

## Newsletter admin

Ver [newsletter.md](./newsletter.md): cada fila indica si se envió a Mailchimp, Audience, group y tags.  
`POST /newsletter/{id}/resync/` reintenta un alta fallida.
