# Admin — Recursos de curso

Archivos descargables (PDF, imagen u otro) asociados a un **curso online**. Se suben al mismo storage que las portadas (Firebase si está configurado). **No** se exponen en el catálogo público: el alumno solo los lista y descarga con `AccessGrant` activo.

Los cursos `format=in_person` no admiten recursos.

**Auth:** JWT `type=staff`

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/admin/courses/{slug}/resources/` | Listar recursos del curso |
| POST | `/admin/courses/{slug}/resources/` | Subir recurso (`multipart/form-data`) |
| GET | `/admin/resources/{id}/` | Detalle |
| PATCH | `/admin/resources/{id}/` | Actualizar metadatos o reemplazar archivo |
| DELETE | `/admin/resources/{id}/` | Eliminar |
| GET | `/admin/resources/{id}/file/` | Descargar el archivo |

Alumno: [`GET /me/courses/{id}/resources/`](../../me/content.md)

## Subir recurso

```http
POST /api/v1/admin/courses/{slug}/resources/
Content-Type: multipart/form-data
Authorization: Bearer <access_staff>
```

| Campo | Tipo | Notas |
|-------|------|-------|
| `file` | file | PDF, imagen u otro archivo. Obligatorio al crear |
| `kind` | `pdf` \| `image` \| `file` | Opcional; si se omite se infiere por extensión/`Content-Type` |
| `sort_order` | int | Orden en el listado (default 0) |
| `is_active` | bool | Inactivo no sale en `/me/` (default true) |
| `translations` | JSON string | Al menos una; `title` obligatorio |

```
file=<archivo.pdf>
kind=pdf
sort_order=0
translations=[{"language_code":"es","title":"Guía de recetas","description":"PDF descargable"}]
```

## Response 201

```json
{
  "data": {
    "id": "uuid",
    "course_id": "uuid",
    "kind": "pdf",
    "original_name": "guia.pdf",
    "content_type": "application/pdf",
    "sort_order": 0,
    "is_active": true,
    "download_url": "http://localhost:8000/api/v1/admin/resources/{id}/file/",
    "translations": [
      {
        "id": "uuid",
        "language_code": "es",
        "title": "Guía de recetas",
        "description": "PDF descargable"
      }
    ],
    "created_at": "2026-08-17T12:00:00Z",
    "updated_at": "2026-08-17T12:00:00Z"
  },
  "meta": {}
}
```

`download_url` apunta a la API admin, **no** a una URL pública de Firebase. Los blobs de recursos no se marcan públicos en Storage.

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 404 | `COURSE_NOT_FOUND` | Slug de curso inexistente |
| 404 | `RESOURCE_NOT_FOUND` | Recurso inexistente |
| 422 | `IN_PERSON_NO_RESOURCES` | El curso es presencial |
| 422 | `TRANSLATIONS_REQUIRED` / `TRANSLATION_TITLE_REQUIRED` | Traducciones inválidas |
| 422 | `LANGUAGE_NOT_FOUND` | Idioma inexistente |
