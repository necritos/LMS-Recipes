# Admin — Sliders

Hero del home: imagen de fondo, título, texto, enlace y texto del enlace.

`POST /api/v1/admin/site/sliders/` — JSON o `multipart/form-data` (imagen).

```json
{
  "title": "Curso de pasta",
  "text": "Aprende desde cero",
  "link": "/cursos/pasta",
  "link_text": "Ver curso",
  "sort_order": 0,
  "is_active": true
}
```

Subir imagen:

```http
POST /api/v1/admin/site/sliders/
Content-Type: multipart/form-data

title=Curso de pasta
background_image=<archivo>
```

Público: solo `is_active=true`, en `GET /api/v1/public/site/`.
