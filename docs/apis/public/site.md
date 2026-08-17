# GET /api/v1/public/site/

Payload del home filtrado por idioma (`?lang=es` default).

Solo aparecen sliders, botones y referencias **activos** y **con traducción** en ese idioma.

## Query

| Param | Default | Descripción |
|-------|---------|-------------|
| `lang` | `es` | Código de idioma activo |

## Response 200

```json
{
  "data": {
    "about": { "title": "Sobre mí", "html": "<p>…</p>" },
    "terms": { "title": "Términos y condiciones", "html": "<p>…</p>" },
    "privacy": { "title": "Política de privacidad", "html": "<p>…</p>" },
    "contracting": { "title": "Condiciones de contratación", "html": "<p>…</p>" },
    "contact_info": { "phone_1": "+421 111", "phone_2": "", "email": "hola@petralicious.sk" },
    "social": { "instagram": "https://instagram.com/...", "tiktok": "", "facebook": "", "pinterest": "" },
    "sliders": [
      {
        "id": "uuid",
        "title": "Aprende pasta",
        "text": "Subtítulo",
        "link": "/cursos",
        "link_text": "Ver cursos",
        "sort_order": 0,
        "background_image_url": "https://…"
      }
    ],
    "start_buttons": [],
    "testimonials": []
  },
  "meta": {}
}
```

`contact_info` y `social` no se traducen (datos de contacto globales).
Sobre mí, textos legales (términos, privacidad, contratación), sliders, botones y referencias sí.

Si el idioma no existe o está inactivo: `404 LANGUAGE_NOT_FOUND`.
