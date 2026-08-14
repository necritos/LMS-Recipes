# Admin — Sliders

Imagen, orden y estado son globales. **Título, texto, enlace y texto del enlace** van por idioma.

```json
{
  "sort_order": 0,
  "is_active": true,
  "translations": [
    {
      "language_code": "es",
      "title": "Curso de pasta",
      "text": "Aprende desde cero",
      "link": "/cursos/pasta",
      "link_text": "Ver curso"
    },
    {
      "language_code": "en",
      "title": "Pasta course",
      "text": "Learn from scratch",
      "link": "/courses/pasta",
      "link_text": "See course"
    }
  ]
}
```

Multipart: `translations` como string JSON + `background_image`.

Público: `GET /api/v1/public/site/?lang=es` — solo activos con traducción en ese idioma.
