# Recetario Backend

Backend REST API (Django + DRF) para plataforma LMS + E-commerce de cursos y recetas.

**Alcance:** solo APIs JSON. El frontend vive en `RECETARIO-FRONTEND`.

## Requisitos

- Python 3.12+
- SQLite (local, default) o PostgreSQL (CI/prod)
- Redis (opcional local, para Celery)

## Inicio rápido

```bash
cp .env.example .env
make install
make migrate
make run
```

- Health check: http://127.0.0.1:8000/health/
- API ping: http://127.0.0.1:8000/api/v1/public/ping/
- OpenAPI: http://127.0.0.1:8000/api/docs/

## Comandos

| Comando | Descripción |
|---------|-------------|
| `make install` | Instala dependencias dev |
| `make run` | Servidor de desarrollo |
| `make migrate` | Aplica migraciones |
| `make test` | Ejecuta pytest |
| `make lint` | Ruff lint + format check |
| `make up` | Levanta Redis (docker compose) |

## Documentación

- [Plan de desarrollo](docs/PLAN-DESARROLLO.md)
- [Arquitectura](docs/BACKEND-ARQUITECTURA.md)
- [Documentación API](docs/apis/README.md)

## Crear admin staff

```bash
python manage.py createsuperuser
```
