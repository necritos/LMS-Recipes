# GET /api/v1/public/site/

Payload del home: sobre mí, redes, teléfonos, sliders, botones «por dónde empezar» y referencias.

Sin autenticación.

## Response 200

```json
{
  "data": {
    "about": {
      "title": "Sobre mí",
      "html": "<p>Texto editable en HTML</p>"
    },
    "contact_info": {
      "phone_1": "+421 111 222",
      "phone_2": "",
      "email": "hola@petralicious.sk"
    },
    "social": {
      "instagram": "https://instagram.com/...",
      "tiktok": "",
      "facebook": "",
      "pinterest": ""
    },
    "sliders": [
      {
        "id": "uuid",
        "title": "Aprende pasta",
        "text": "Subtítulo",
        "link": "/cursos",
        "link_text": "Ver cursos",
        "sort_order": 0,
        "background_image_url": "https://firebasestorage.googleapis.com/..."
      }
    ],
    "start_buttons": [
      {
        "id": "uuid",
        "color": "#C45C26",
        "title": "Cursos",
        "link": "/cursos",
        "link_text": "Empezar",
        "sort_order": 0,
        "image_url": "https://..."
      }
    ],
    "testimonials": [
      {
        "id": "uuid",
        "stars": 5,
        "comment": "Excelente contenido",
        "name": "Ana",
        "sort_order": 0
      }
    ]
  },
  "meta": {}
}
```

Solo se incluyen sliders, botones y referencias con `is_active=true`.
Las imágenes salen de Firebase Storage si el admin lo activó; si no, URL local.
