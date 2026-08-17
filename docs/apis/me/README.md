# Me — Usuario autenticado

JWT `type=user` vía `POST /auth/login/`. Prefijo `/api/v1/me/`.

| Documento | Endpoints |
|-----------|-----------|
| [cart.md](./cart.md) | `GET/POST/DELETE /me/cart/`, `DELETE /me/cart/items/{id}/` |
| [purchases.md](./purchases.md) | `GET /me/purchases/` |
| [library.md](./library.md) | `GET /me/courses/`, `GET /me/recipes/` |
| [progress.md](./progress.md) | `POST /me/lessons/{id}/view/`, `POST /me/lessons/{id}/complete/`, `GET /me/progress/{course_id}/` |
| [content.md](./content.md) | `GET /me/courses/{id}/lessons/`, `GET /me/courses/{id}/resources/`, `GET /me/recipes/{id}/`, `GET /me/recipes/{id}/video/` |
