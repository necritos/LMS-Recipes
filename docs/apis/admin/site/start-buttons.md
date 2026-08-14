# Admin — Por dónde empezar

Botones del home: color, imagen, título, enlace y texto del enlace.

`POST /api/v1/admin/site/start-buttons/`

```json
{
  "color": "#C45C26",
  "title": "Cursos",
  "link": "/cursos",
  "link_text": "Empezar",
  "sort_order": 0,
  "is_active": true
}
```

`color` en hexadecimal (`#RGB` o `#RRGGBB`). Imagen vía multipart campo `image`.
