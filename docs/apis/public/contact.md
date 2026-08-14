# POST /api/v1/public/contact/

Formulario «Contáctanos». Sin autenticación.

## Request

```json
{
  "name": "María García",
  "email": "maria@example.com",
  "topic": "Información de cursos",
  "message": "Quiero saber fechas de inicio."
}
```

## Response 201

```json
{
  "data": { "message": "Mensaje enviado correctamente." },
  "meta": {}
}
```

El staff lo ve en `GET /api/v1/admin/contact/` y puede marcarlo como leído.
