# Plan de Desarrollo — Recetario Backend (API)

**Proyecto:** Backend REST API para plataforma LMS + E-commerce (cursos y recetas)  
**Alcance:** **Solo backend y APIs** — sin frontend, UI, HTML, CSS ni JavaScript  
**Referencia arquitectónica:** [BEDERR-BACKEND](/Users/admin/Desktop/projects/BEDERR-BACKEND)  
**Despliegue objetivo:** Digital Ocean  
**Duración estimada:** 8 semanas  
**Versión:** 1.1 — Junio 2026

---

## 1. Resumen del producto

Este repositorio desarrolla el **backend Django/DRF** que expone APIs REST para una plataforma LMS + E-commerce. El frontend es un proyecto separado (`RECETARIO-FRONTEND`) y **no forma parte de este alcance**.

### APIs que entrega este backend

- Multi-idioma: endpoints de catálogo filtrables por idioma
- Autenticación: registro, login JWT, Google OAuth, reset password
- Catálogo público: cursos y recetas (listado, detalle, categorías)
- E-commerce: carrito, checkout Stripe, webhooks de pago
- Acceso a contenido: cursos (1 año) y recetas (lifetime o 1 año)
- Video: URLs firmadas vía Bunny.net (el cliente frontend las consume)
- Admin API: CRUD de contenido, usuarios, dashboard financiero (JSON)
- Notificaciones: emails transaccionales (HTML mínimo en templates de email)

### Fuera de alcance de este repo

Ver sección 9. En resumen: landing page, diseño responsive, reproductor embebido, paneles visuales, checkout UI, carrito UI, SEO en HTML, footer, etc.

---

## 2. Stack tecnológico

| Componente | Elección | Notas |
|------------|----------|-------|
| Python | 3.12+ | `.python-version` |
| Django | 5.x | |
| DRF | 3.15+ | API REST |
| Auth | `djangorestframework-simplejwt` + Google OAuth | Staff y usuarios finales |
| OpenAPI | `drf-spectacular` | `/api/schema/` |
| BD local | **SQLite** (default Django) | Sin Docker obligatorio en dev |
| BD prod | **PostgreSQL 16** | Digital Ocean Managed Database |
| Cache/Queue | Redis 7 | Celery broker (Managed Redis en DO) |
| Tareas async | Celery | Emails, webhooks, expiración de accesos |
| Storage prod | Digital Ocean Spaces | S3-compatible (imágenes, assets) |
| Video hosting | Bunny.net Stream | URLs firmadas, sin descarga |
| Pagos | Stripe | Checkout + webhooks |
| Email | SendGrid o Resend | Transaccional |
| Servidor prod | Gunicorn + WhiteNoise | App Platform o Droplet |
| Calidad | Ruff + pytest | Igual que BEDERR |
| CI/CD | GitHub Actions | Tests + deploy a DO |

---

## 3. Arquitectura de despliegue (Digital Ocean)

```mermaid
flowchart TB
    subgraph Internet
        FE[Frontend externo - fuera de alcance]
        Stripe[Stripe Webhooks]
    end

    subgraph DigitalOcean["Digital Ocean"]
        LB[App Platform / Load Balancer]
        API[Django API - Gunicorn]
        Worker[Celery Worker]
        PG[(Managed PostgreSQL)]
        Redis[(Managed Redis)]
        Spaces[DO Spaces - Media]
    end

    subgraph External
        Bunny[Bunny.net Stream]
        Google[Google OAuth]
        Email[SendGrid / Resend]
    end

    FE -->|REST JSON| LB --> API
    API --> PG
    API --> Redis
    Worker --> PG
    Worker --> Redis
    API --> Spaces
    API --> Bunny
    API --> Google
    Worker --> Email
    Stripe --> API
```

### Entornos

| Entorno | BD | Storage | Redis |
|---------|-----|---------|-------|
| **Local** | SQLite (`db.sqlite3`) | Filesystem local | Opcional (docker-compose) |
| **Staging** | PostgreSQL (DO) | Spaces | Managed Redis |
| **Producción** | PostgreSQL (DO) | Spaces | Managed Redis |

### Variables de entorno clave

```bash
# Django
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=
DJANGO_SETTINGS_MODULE=config.settings.production

# Base de datos
DATABASE_URL=postgres://user:pass@host:25060/recetario?sslmode=require

# Redis / Celery
CELERY_BROKER_URL=rediss://...
CELERY_RESULT_BACKEND=rediss://...

# Stripe
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PUBLISHABLE_KEY=

# Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Bunny.net
BUNNY_STREAM_LIBRARY_ID=
BUNNY_STREAM_API_KEY=
BUNNY_STREAM_CDN_HOSTNAME=

# Storage (DO Spaces)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
AWS_S3_REGION_NAME=nyc3

# Email
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

# CORS (dominios del frontend externo, no desarrollado aquí)
CORS_ALLOWED_ORIGINS=https://recetario.com
```

---

## 4. Estructura del repositorio

```
recetario-backend/
├── .cursor/rules/              # Reglas Cursor (ver sección 12)
├── .env.example
├── .github/workflows/          # ci.yml, deploy.yml
├── docker-compose.yml          # Redis local (Postgres opcional)
├── Dockerfile
├── Makefile
├── pyproject.toml
├── manage.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py            # SQLite default
│   │   ├── test.py
│   │   └── production.py       # PostgreSQL + Spaces
│   ├── urls.py
│   ├── api_urls.py
│   ├── celery.py
│   └── wsgi.py
├── apps/
│   ├── common/                 # Base models, permissions, pagination, errors
│   ├── accounts/               # User, Staff, JWT, Google OAuth
│   ├── catalog/                # Course, Recipe, Category, Language, Pricing
│   ├── commerce/               # Cart, Order, Stripe, webhooks
│   ├── content/                # Lesson, Module, VideoAccess, progress
│   ├── notifications/          # Email templates + Celery tasks
│   └── analytics/              # Dashboard stats, sales reports
├── deploy/
│   ├── docker-entrypoint.sh
│   └── env.digitalocean.example
├── docs/
│   ├── PLAN-DESARROLLO.md      # Este documento
│   └── BACKEND-ARQUITECTURA.md
└── tests/
```

### Convención por app (heredada de BEDERR)

```
apps/<app>/
├── models.py
├── selectors.py          # Consultas de lectura
├── services/             # Lógica de negocio (escrituras)
├── api/
│   ├── public/           # Catálogo y datos públicos (JSON)
│   ├── admin/            # APIs administración
│   └── me/               # APIs usuario autenticado
├── migrations/
└── tests/
```

---

## 5. Modelo de dominio (resumen)

### Entidades principales

| Modelo | Descripción |
|--------|-------------|
| `Language` | Idiomas disponibles (es, en, fr...) |
| `Category` | Categorías de cursos/recetas |
| `Course` | Curso con precio, duración acceso (365 días), traducciones |
| `Recipe` | Receta con precio, acceso lifetime o 365 días |
| `Module` / `Lesson` | Estructura del curso + video Bunny ID |
| `Cart` / `CartItem` | Carrito de compras |
| `Order` / `OrderItem` | Pedido completado |
| `Purchase` / `AccessGrant` | Acceso del usuario con fecha expiración |
| `VideoAccessToken` | Token firmado temporal para Bunny.net |
| `StaffUser` | Admin (API staff) |
| `UserAccount` | Cliente / estudiante |

### Reglas de negocio clave

1. **Cursos:** acceso válido 1 año desde la compra
2. **Recetas:** acceso de por vida O 1 año (configurable por producto)
3. **Videos:** solo reproducibles con token autenticado; sin descarga directa
4. **Pagos:** confirmación vía webhook Stripe antes de otorgar acceso
5. **Idiomas:** contenido filtrable; traducciones en modelos relacionados o JSONField i18n

---

## 6. API — Estructura de endpoints

Prefijo base: `/api/v1/`

| Prefijo | Audiencia | Ejemplos |
|---------|-----------|----------|
| `/api/v1/public/` | Visitantes | Catálogo, detalle curso/receta, idiomas |
| `/api/v1/auth/` | Registro/login | login, register, Google OAuth, reset password |
| `/api/v1/me/` | Usuario autenticado | Mis cursos, mis recetas, carrito, perfil |
| `/api/v1/checkout/` | Usuario autenticado | Crear sesión Stripe, confirmar pago |
| `/api/v1/admin/` | Staff | CRUD cursos/recetas, usuarios, dashboard |
| `/api/v1/webhooks/stripe/` | Stripe | Eventos de pago |

### Contrato de respuesta (heredado de BEDERR)

```json
// Éxito (recurso único)
{ "data": { ... }, "meta": {} }

// Lista paginada
{ "count": 100, "next": "...", "previous": null, "results": [] }

// Error
{ "error": { "code": "ACCESS_EXPIRED", "message": "Tu acceso ha expirado.", "details": {} } }
```

---

## 7. Plan de trabajo por fases (8 semanas)

> Marca cada ítem con `[x]` al completarlo. Ejemplo: `- [x] Tarea terminada`

### Progreso general

| Fase | Semana | Estado |
|------|--------|--------|
| 0 — Fundación | 1 | ✅ Completada |
| 1 — Autenticación | 2 | ✅ Completada |
| 2 — Catálogo | 3 | ⬜ Pendiente |
| 3 — Contenido y video | 4 | ⬜ Pendiente |
| 4 — E-commerce | 5 | ⬜ Pendiente |
| 5 — APIs usuario | 6 | ⬜ Pendiente |
| 6 — Admin y analytics | 7 | ⬜ Pendiente |
| 7 — Despliegue y QA | 8 | ⬜ Pendiente |

---

### Fase 0 — Fundación (Semana 1)

**Objetivo:** Repositorio arrancable con convenciones BEDERR.

#### Checklist

- [x] Inicializar proyecto Django (`manage.py`, estructura `config/`, `apps/`)
- [x] Crear `pyproject.toml` con dependencias base (Django, DRF, pytest, ruff)
- [x] Configurar settings split: `base.py`, `local.py`, `test.py`, `production.py`
- [x] BD local: SQLite como default en `local.py`
- [x] BD prod: parser `DATABASE_URL` para PostgreSQL en `production.py`
- [x] Crear app `common` con `UUIDModel` y `TimeStampedModel`
- [x] Implementar paginación por defecto (`DefaultPageNumberPagination`)
- [x] Implementar exception handler y envelope renderer JSON
- [x] Crear endpoint health check (`GET /health/`)
- [x] Crear `docker-compose.yml` con Redis (Postgres opcional)
- [x] Crear `Makefile` con comandos `run`, `test`, `lint`, `migrate`
- [x] Crear `.env.example` con variables documentadas
- [x] Configurar CI en GitHub Actions (ruff + pytest con PostgreSQL)
- [x] Escribir tests básicos de `common` y health check
- [x] Documentar arquitectura en `docs/BACKEND-ARQUITECTURA.md`

#### Criterio de aceptación

- [x] `pytest` pasa en local
- [x] `make run` levanta el servidor sin errores
- [x] API health check responde `200`

**Fase completada:** ✅

---

### Fase 1 — Autenticación y usuarios (Semana 2)

**Objetivo:** Registro, login, Google OAuth, recuperación de contraseña.

#### Checklist

- [x] Crear app `accounts` con modelos `UserAccount` y `StaffUser`
- [x] Configurar JWT dual (type `user` / `staff`) con SimpleJWT
- [x] Endpoint `POST /api/v1/auth/register/`
- [x] Endpoint `POST /api/v1/auth/login/`
- [x] Endpoint `POST /api/v1/auth/refresh/` y logout con blacklist
- [x] Endpoint `POST /api/v1/admin/auth/login/` para staff
- [x] Integrar Google OAuth (`POST /api/v1/auth/google/`)
- [x] Flujo password reset: solicitud + confirmación con token
- [x] Template email recuperación de contraseña
- [x] Permisos DRF: `IsStaffUser`, `IsAuthenticatedUser`
- [x] Configurar CORS (`django-cors-headers`)
- [x] Configurar Celery + Redis para tareas async
- [x] Task Celery: email de bienvenida al registrarse
- [x] Tests de registro, login, OAuth y reset password
- [x] Documentación API en `docs/apis/auth/` y `docs/apis/admin/`

#### Criterio de aceptación

- [x] Usuario se registra e inicia sesión con email/contraseña
- [x] Usuario inicia sesión con Google OAuth
- [x] Staff accede a las APIs admin con JWT propio
- [x] Email de bienvenida se envía (o queda en cola Celery)

**Fase completada:** ✅

---

### Fase 2 — Catálogo multi-idioma (Semana 3)

**Objetivo:** CRUD de cursos, recetas, categorías e idiomas.

#### Checklist

- [ ] Crear app `catalog`
- [ ] Modelo `Language` (código, nombre, activo)
- [ ] Modelo `Category` con soporte multi-idioma
- [ ] Modelo `Course` (precio, slug, duración acceso 365 días, traducciones)
- [ ] Modelo `Recipe` (precio, slug, acceso lifetime/365 días, traducciones)
- [ ] Migraciones y datos seed de idiomas (ES, EN mínimo)
- [ ] API pública: `GET /api/v1/public/courses/` con filtro `?lang=`
- [ ] API pública: `GET /api/v1/public/recipes/` con filtro `?lang=`
- [ ] API pública: detalle por slug (`/public/courses/{slug}/`)
- [ ] API admin: CRUD completo de cursos
- [ ] API admin: CRUD completo de recetas
- [ ] API admin: gestión de categorías e idiomas
- [ ] Upload de imágenes de portada (local en dev)
- [ ] Configurar storage DO Spaces en `production.py`
- [ ] Campos SEO: slug único, meta title, meta description
- [ ] Tests de catálogo público y CRUD admin

#### Criterio de aceptación

- [ ] Admin crea curso en ES y EN
- [ ] Catálogo público filtra correctamente por idioma
- [ ] Imágenes de portada se suben y sirven correctamente

**Fase completada:** ⬜

---

### Fase 3 — Contenido y video (Semana 4)

**Objetivo:** Lecciones, módulos e integración Bunny.net.

#### Checklist

- [ ] Crear app `content`
- [ ] Modelo `Module` (pertenece a Course, orden)
- [ ] Modelo `Lesson` (pertenece a Module, `bunny_video_id`, orden)
- [ ] Asociar video único a `Recipe` (`bunny_video_id`)
- [ ] Servicio `VideoAccessService` con tokens firmados y expiración
- [ ] Integración API Bunny.net (library ID, API key en env)
- [ ] API `GET /api/v1/me/courses/{id}/lessons/` con URL de video
- [ ] API `GET /api/v1/me/recipes/{id}/video/` con URL de video
- [ ] Permiso `HasActiveAccess`: verificar Purchase/AccessGrant activo
- [ ] Respuesta 403 si acceso expirado o inexistente
- [ ] Admin: asociar/editar `bunny_video_id` en lecciones
- [ ] Admin: asociar/editar `bunny_video_id` en recetas
- [ ] Tests de acceso autorizado vs denegado y expiración de token

#### Criterio de aceptación

- [ ] API devuelve URL firmada de video si el usuario tiene acceso activo
- [ ] API responde 403 si no hay acceso o está expirado
- [ ] URL de video expira tras el TTL configurado

**Fase completada:** ⬜

---

### Fase 4 — E-commerce y Stripe (Semana 5)

**Objetivo:** Carrito, checkout y webhooks.

#### Checklist

- [ ] Crear app `commerce`
- [ ] Modelos `Cart`, `CartItem`, `Order`, `OrderItem`
- [ ] Modelos `Purchase` y `AccessGrant` con `expires_at`
- [ ] API carrito: `GET/POST/PATCH/DELETE /api/v1/me/cart/`
- [ ] Servicio `CheckoutService.create_stripe_session()`
- [ ] Endpoint `POST /api/v1/checkout/create-session/`
- [ ] Configurar Stripe test keys en `.env`
- [ ] Webhook `POST /api/v1/webhooks/stripe/` con verificación de firma
- [ ] Handler `checkout.session.completed` → crear Order + AccessGrant
- [ ] Idempotencia: no procesar el mismo `event.id` dos veces
- [ ] Habilitar Apple Pay y Google Pay en Stripe Checkout
- [ ] Crear app `notifications` con template email confirmación de compra
- [ ] Task Celery: enviar email al completar compra
- [ ] Tests de carrito, checkout y webhook (Stripe test mode)

#### Criterio de aceptación

- [ ] Compra test en Stripe sandbox otorga acceso al producto
- [ ] Email de confirmación de compra enviado
- [ ] Webhook rechaza requests sin firma válida

**Fase completada:** ⬜

---

### Fase 5 — APIs de usuario (Semana 6)

**Objetivo:** Endpoints de compras, acceso a contenido y progreso (JSON).

#### Checklist

- [ ] API `GET /api/v1/me/purchases/` — listado de compras
- [ ] API `GET /api/v1/me/courses/` — cursos con acceso activo y fecha expiración
- [ ] API `GET /api/v1/me/recipes/` — recetas con acceso activo y fecha expiración
- [ ] Modelo `LessonProgress` (usuario, lección, completada, última vista)
- [ ] API `POST /api/v1/me/lessons/{id}/complete/` — marcar lección completada
- [ ] API `GET /api/v1/me/progress/{course_id}/` — progreso del curso
- [ ] Regla: cursos expiran a los 365 días desde compra
- [ ] Regla: recetas respetan lifetime o 365 días según producto
- [ ] Task Celery `expire_access_grants` — marcar accesos vencidos
- [ ] Programar job diario (cron / App Platform job)
- [ ] API "continuar viendo": última lección vista por curso
- [ ] Tests de expiración de acceso y progreso de lecciones

#### Criterio de aceptación

- [ ] APIs `/me/` devuelven productos comprados con fechas de expiración
- [ ] Endpoints de contenido responden 403 tras expiración de acceso
- [ ] Progreso de lecciones se persiste y se expone vía API

**Fase completada:** ⬜

---

### Fase 6 — Admin y analytics (Semana 7)

**Objetivo:** APIs de dashboard financiero y gestión administrativa (JSON).

#### Checklist

- [ ] Crear app `analytics`
- [ ] API `GET /api/v1/admin/dashboard/` — resumen general
- [ ] Métrica: ingresos totales y por período (día/semana/mes)
- [ ] Métrica: ventas recientes (últimas N órdenes)
- [ ] Métrica: productos más vendidos
- [ ] API `GET /api/v1/admin/users/` — listado paginado
- [ ] API `GET /api/v1/admin/users/{id}/` — detalle con historial de compras
- [ ] API gestión idiomas: activar/desactivar (`/admin/languages/`)
- [ ] Documentar config Stripe (keys solo en env; toggle test/live documentado)
- [ ] Endpoint `GET /api/v1/admin/dashboard/revenue/` — serie temporal ingresos (JSON)
- [ ] Tests de dashboard y endpoints admin

#### Criterio de aceptación

- [ ] API dashboard devuelve ingresos reales calculados desde `Order`
- [ ] Admin puede listar usuarios y ver sus compras
- [ ] Estadísticas coinciden con datos de `Order` en BD

**Fase completada:** ⬜

---

### Fase 7 — Despliegue y QA (Semana 8)

**Objetivo:** Producción en Digital Ocean + pruebas finales.

#### Checklist

**Infraestructura**

- [ ] Crear `Dockerfile` production-ready
- [ ] Crear `deploy/docker-entrypoint.sh` (API, worker, migrate job)
- [ ] Crear `deploy/env.digitalocean.example`
- [ ] Provisionar Managed PostgreSQL en Digital Ocean
- [ ] Provisionar Managed Redis en Digital Ocean
- [ ] Provisionar DO Spaces para media
- [ ] Desplegar App Platform: servicio web (Gunicorn)
- [ ] Desplegar App Platform: worker Celery (componente separado)
- [ ] Configurar job de migraciones pre-deploy
- [ ] Configurar dominio del cliente en App Platform
- [ ] Verificar SSL/HTTPS activo (Let's Encrypt)

**Integraciones producción**

- [ ] Variables de entorno en App Platform (SECRET_KEY, DATABASE_URL, etc.)
- [ ] Webhook Stripe apuntando a URL pública de producción
- [ ] Stripe en modo live (o test según acuerdo con cliente)
- [ ] Email transaccional producción (SendGrid/Resend)
- [ ] Bunny.net configurado con credenciales de producción

**QA y cierre (solo API — vía pytest y requests manuales)**

- [ ] Test integración API: registro → checkout → webhook → acceso a curso/receta
- [ ] Test integración API: endpoint de video responde 200/403 según acceso
- [ ] Test integración API: admin crea curso y aparece en catálogo público
- [ ] Test integración: email confirmación de compra enviado (Celery)
- [ ] Verificar accesos expiran según reglas (curso 1 año / receta lifetime)
- [ ] Publicar OpenAPI en `/api/schema/` y `/api/docs/` (Swagger/Redoc)
- [ ] Documento QA API / checklist pre-lanzamiento (sección 11) completado
- [ ] Entrega código fuente backend al cliente

#### Criterio de aceptación

- [ ] API accesible en dominio/staging vía HTTPS
- [ ] Flujo compra vía API + Stripe sandbox funciona end-to-end
- [ ] Celery worker procesa emails y jobs en producción

**Fase completada:** ⬜

---

## 8. Hitos de pago (alineados al presupuesto)

| Hito | % | Semana | Entregable |
|------|---|--------|------------|
| Inicio | 50% | 0 | Fase 0 completa + plan aprobado |
| Versión de prueba | 25% | 4–5 | APIs catálogo + auth + video + checkout sandbox |
| Producción | 25% | 8 | API en DO + dominio + SSL + OpenAPI |

---

## 9. Fuera de alcance

### Frontend e interfaz (no se desarrolla en este repo)

- Landing page, diseño visual y manual de marca en UI
- Cualquier HTML/CSS/JavaScript de la aplicación web
- Reproductor de video embebido (iframe/player en browser)
- Carrito, checkout y paneles de usuario **como interfaz gráfica**
- Panel de administración **como interfaz gráfica** (solo existen APIs admin)
- Diseño responsive, componentes React/Vue, etc.
- Footer, créditos visuales del desarrollador en UI
- SEO en HTML (meta tags renderizados en frontend)
- Proyecto `RECETARIO-FRONTEND` y templates HTML de referencia (`RECETARIO-TEMPLATES/`)

### Contenido y operación (cliente / otros proyectos)

- Grabación, edición y subida de videos a Bunny.net (cliente)
- Redacción de contenidos y traducciones (cliente)
- Dominio y hosting del frontend (costo real del cliente)
- Marketing digital / SEO avanzado
- Integraciones no mencionadas en el presupuesto

### Lo que sí incluye este backend

- Templates **de email** transaccional (HTML mínimo para correos)
- OpenAPI/Swagger como documentación de la API
- Configuración CORS para que un frontend externo consuma la API
- URLs firmadas de video (el frontend las usa; el player no se implementa aquí)

---

## 10. Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Retraso en contenidos del cliente | Desarrollo con fixtures/dummy data |
| Costos Bunny.net imprevistos | Documentar estimación; lazy load videos |
| Complejidad multi-idioma | MVP con 2 idiomas; arquitectura extensible |
| Webhooks Stripe en local | Stripe CLI para dev; staging en DO |
| SQLite vs PostgreSQL diffs | Tests CI siempre en PostgreSQL |

---

## 11. Checklist pre-lanzamiento

- [ ] `SECRET_KEY` y keys Stripe en variables de entorno (nunca en repo)
- [ ] `DEBUG=False` en producción
- [ ] CORS restringido a dominios del frontend externo (config only)
- [ ] Webhooks Stripe verificados con signing secret
- [ ] Backups PostgreSQL automáticos (DO Managed DB)
- [ ] Celery worker corriendo en producción
- [ ] Emails transaccionales probados
- [ ] URLs de video firmadas y con TTL; sin exposición pública del `bunny_video_id`
- [ ] Accesos expiran correctamente (job Celery)
- [ ] SSL activo + redirect HTTP→HTTPS
- [ ] OpenAPI documentada en `/api/schema/`

---

## 12. Reglas Cursor

Las reglas de desarrollo para agentes y desarrolladores están en:

```
.cursor/rules/
├── project-overview.mdc      # Contexto global (alwaysApply)
├── django-architecture.mdc   # Capas, apps, servicios
├── api-conventions.mdc       # DRF, serializers, errores
├── database-settings.mdc     # SQLite local / PostgreSQL prod
└── deployment-digitalocean.mdc
```

---

## 13. Referencias

- Arquitectura base: `BEDERR-BACKEND/docs/BACKEND-ARQUITECTURA-Y-LINEAMIENTOS.md`
- Frontend (proyecto separado): `../RECETARIO-FRONTEND/`
- Mockups UI solo referencia visual (no desarrollo): `../RECETARIO-TEMPLATES/`
- [Digital Ocean App Platform](https://docs.digitalocean.com/products/app-platform/)
- [Bunny.net Stream API](https://docs.bunny.net/docs/stream)
- [Stripe Checkout](https://stripe.com/docs/checkout)
