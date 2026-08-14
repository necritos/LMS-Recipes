# POST /api/v1/public/newsletter/

Alta de email al newsletter. Sin autenticación.

## Request

```json
{ "email": "ana@example.com" }
```

## Response 201

```json
{
  "data": { "message": "Suscripción registrada." },
  "meta": {}
}
```

## Errores

| HTTP | code | Cuándo |
|------|------|--------|
| 409 | `EMAIL_ALREADY_SUBSCRIBED` | Email ya registrado |

Listado staff: `GET /api/v1/admin/newsletter/`.
