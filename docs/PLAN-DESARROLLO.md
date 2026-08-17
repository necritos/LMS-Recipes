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
- Cursos online (módulos, lecciones, recursos) y presenciales (fecha, dirección, Maps)
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
| Storage prod | Firebase Storage (admin) / DO Spaces fallback | Imágenes públicas |
| Video hosting | Bunny.net Stream | URLs firmadas, sin descarga |
| Pagos | Stripe | Checkout + webhooks |
| Email | Mailchimp | Marketing API (newsletter) + Transactional/Mandrill (bienvenida, reset, compra). Config en admin |
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
        Email[Mailchimp]
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

# Google OAuth: preferible admin PATCH /api/v1/admin/site/google/
# Fallback legacy (solo si google_oauth_enabled=false):
# GOOGLE_CLIENT_ID=

# Stripe, Bunny.net, Firebase, Mailchimp y Google OAuth: credenciales en admin (nunca en .env)
# Guía: docs/configurar-integraciones.md
# PATCH /api/v1/admin/site/stripe/
# PATCH /api/v1/admin/site/bunny/
# PATCH /api/v1/admin/site/settings/
# PATCH /api/v1/admin/site/mailchimp/
# PATCH /api/v1/admin/site/google/

# Storage (DO Spaces)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
AWS_S3_REGION_NAME=nyc3

# Email: en producción se usa Mailchimp (admin). Fallback local SMTP:
# EMAIL_HOST=
# EMAIL_HOST_USER=
# EMAIL_HOST_PASSWORD=
# DEFAULT_FROM_EMAIL=

# CORS (dominios del frontend; en prod además hay wildcards en production.py)
CORS_ALLOWED_ORIGINS=https://petralicious.sk
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
│   ├── site/                   # CMS home, Firebase storage config, contacto, newsletter
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
| `/api/v1/public/` | Visitantes | Catálogo, detalle curso/receta, idiomas, home, contacto, newsletter |
| `/api/v1/auth/` | Registro/login | login, register, Google OAuth, reset password |
| `/api/v1/me/` | Usuario autenticado | Carrito, compras, biblioteca, progreso, video firmado |
| `/api/v1/checkout/` | Usuario autenticado | Crear sesión Stripe Checkout |
| `/api/v1/admin/` | Staff | CRUD catálogo, CMS, Firebase, Bunny, Stripe, Mailchimp, Google, usuarios, dashboard |
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
>
> **Mantenimiento:** al implementar features nuevas, adelantar ítems de fases futuras o cerrar una fase, **actualizar este archivo en el mismo PR/cambio** (checklist, criterios, tabla de progreso y sección 6 si cambian endpoints). Regla Cursor: `.cursor/rules/plan-desarrollo-sync.mdc`.

### Progreso general

| Fase | Semana | Estado |
|------|--------|--------|
| 0 — Fundación | 1 | ✅ Completada |
| 1 — Autenticación | 2 | ✅ Completada |
| 2 — Catálogo | 3 | ✅ Completada |
| 2.5 — Sitio / Firebase / contacto | 3 | ✅ Completada |
| 3 — Contenido y video | 4 | ✅ Completada |
| 4 — E-commerce | 5 | ✅ Completada |
| 5 — APIs usuario | 6 | ✅ Completada |
| 6 — Admin y analytics | 7 | ✅ Completada |
| 7 — Despliegue y QA | 8 | 🔄 En curso (Droplet + CI/CD) |

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
- [x] Credenciales Google OAuth vía admin `GET/PATCH /admin/site/google/` (como Firebase; fallback env)
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

**Objetivo:** CRUD de cursos, recetas, categorías e idiomas; catálogo público multi-idioma; listado admin de usuarios.

#### Checklist

- [x] Crear app `catalog`
- [x] Modelo `Language` (código, nombre, activo)
- [x] Modelo `Category` con soporte multi-idioma
- [x] Modelo `Course` (precio, slug, duración acceso 365 días, traducciones)
- [x] Formato de curso `online` \| `in_person` (presencial: fecha/hora, dirección, Google Maps; sin módulos ni recursos)
- [x] API admin `GET /api/v1/admin/courses/{slug}/purchases/` — compradores del curso
- [x] Modelo `Recipe` (precio, slug, acceso lifetime/365 días, traducciones)
- [x] Migraciones y datos seed de idiomas (ES, EN mínimo) — `seed_languages` / `make seed-languages`
- [x] API pública: `GET /api/v1/public/languages/`
- [x] API pública: `GET /api/v1/public/categories/?lang=`
- [x] API pública: `GET /api/v1/public/courses/` con filtro `?lang=`
- [x] API pública: `GET /api/v1/public/recipes/` con filtro `?lang=`
- [x] API pública: detalle por slug (`/public/courses/{slug}/`, `/public/recipes/{slug}/`)
- [x] API admin: CRUD completo de cursos
- [x] API admin: CRUD completo de recetas
- [x] API admin: CRUD categorías e idiomas (incl. activar/desactivar `is_active`)
- [x] API admin: `GET /api/v1/admin/users/` — listado paginado con búsqueda *(adelantado desde Fase 6)*
- [x] API admin: `GET /api/v1/admin/users/{id}/` — detalle básico *(compras: Fase 5)*
- [x] Upload de imágenes de portada (local en dev)
- [x] Configurar storage DO Spaces en `production.py`
- [x] Campos SEO: slug único, meta title, meta description
- [x] Tests de catálogo público, CRUD admin, categorías e idiomas
- [x] Tests listado y detalle admin de usuarios
- [x] Documentación API pública en `docs/apis/public/`
- [x] Documentación admin por recurso: `languages.md`, `categories.md`, `courses.md`, `recipes.md`, `users/`
- [x] Guía del sistema multi-idioma en `docs/apis/admin/catalog/languages.md`

#### Criterio de aceptación

- [x] Admin crea curso en ES y EN
- [x] Admin gestiona categorías, idiomas y recetas vía API
- [x] Catálogo público filtra correctamente por idioma
- [x] Imágenes de portada se suben y sirven correctamente
- [x] Staff puede listar usuarios registrados

**Fase completada:** ✅

---

### Fase 2.5 — Sitio, Firebase Storage, contacto y newsletter

**Objetivo:** CMS del home, storage de imágenes configurable (Firebase) y captación (contacto + newsletter).

#### Checklist

- [x] App `site` con `SiteSettings` (redes, teléfonos, email) y traducciones de «sobre mí»
- [x] Textos legales por idioma: términos y condiciones, política de privacidad, condiciones de contratación
- [x] Firebase Storage configurable por API admin (`PATCH /admin/site/settings/`)
- [x] Storage dinámico: Firebase → DO Spaces → filesystem (todas las ImageField y FileField de recursos)
- [x] CRUD sliders multi-idioma (imagen global; título/texto/enlace por idioma)
- [x] CRUD «por dónde empezar» multi-idioma (color/imagen globales)
- [x] CRUD referencias multi-idioma (estrellas globales; nombre/comentario por idioma)
- [x] API pública `GET /api/v1/public/site/?lang=`
- [x] Formulario contacto `POST /api/v1/public/contact/` + inbox admin leído/no leído
- [x] Newsletter `POST /api/v1/public/newsletter/` + listado admin
- [x] Mailchimp Marketing: Audience + group Idioma + tags (WEB_ES/WEB_SK); config admin *(adelantado; emails transaccionales Mandrill)*
- [x] Tests y documentación en `docs/apis/`

#### Criterio de aceptación

- [x] Admin configura Firebase y el JSON de credenciales no se expone en GET
- [x] Home público filtra sliders, sobre mí, textos legales, botones y referencias por `?lang=` (mismo sistema que el catálogo)
- [x] Contacto se marca como leído en admin; newsletter rechaza emails duplicados
- [x] Newsletter sincroniza a Mailchimp (Audience, group de idioma, tags) y el listado admin muestra destino

**Fase completada:** ✅

---

### Fase 3 — Contenido y video (Semana 4)

**Objetivo:** Lecciones, módulos e integración Bunny.net.

#### Checklist

- [x] Crear app `content`
- [x] Modelo `Module` (pertenece a Course, orden; título por idioma)
- [x] Modelo `Lesson` (pertenece a Module, `bunny_video_id`, orden; título por idioma)
- [x] Traducciones: módulo `description`; lección `description` + `content_html` (HTML solo en `/me/`)
- [x] Receta: `ingredients_html` + `preparation_html` por idioma (solo `GET /me/recipes/{id}/` con acceso)
- [x] Asociar video único a `Recipe` (`bunny_video_id`)
- [x] Servicio de URLs firmadas Bunny con TTL (`sign_bunny_video` + `VideoAccessToken`)
- [x] Credenciales Bunny.net vía admin `GET/PATCH /admin/site/bunny/` (como Firebase; no en env)
- [x] API `GET /api/v1/me/courses/{id}/lessons/` con URL de video
- [x] Recursos de curso (PDF/imagen/archivo) en Firebase; `GET /me/courses/{id}/resources/` solo con AccessGrant
- [x] API `GET /api/v1/me/recipes/{id}/video/` con URL de video
- [x] Permiso `HasActiveAccess`: verificar `AccessGrant` activo *(modelo adelantado desde Fase 4)*
- [x] Respuesta 403 si acceso expirado (`ACCESS_EXPIRED`) o inexistente (`ACCESS_DENIED`)
- [x] Admin: módulos/lecciones y `bunny_video_id` en lecciones
- [x] Admin: asociar/editar `bunny_video_id` en recetas
- [x] Tests de acceso autorizado vs denegado y expiración de token

#### Criterio de aceptación

- [x] API devuelve URL firmada de video si el usuario tiene acceso activo
- [x] API responde 403 si no hay acceso o está expirado
- [x] URL de video expira tras el TTL configurado en admin
- [x] GET de Bunny no expone `bunny_api_key` ni `bunny_token_key`

**Fase completada:** ✅

---

### Fase 4 — E-commerce y Stripe (Semana 5)

**Objetivo:** Carrito, checkout y webhooks.

#### Checklist

- [x] Crear app `commerce`
- [x] Modelos `Cart`, `CartItem`, `Order`, `OrderItem`
- [x] Modelos `Purchase` y `AccessGrant` con `expires_at` *(AccessGrant en Fase 3; Purchase + grants en webhook aquí)*
- [x] API carrito: `GET/POST/DELETE /api/v1/me/cart/` y `DELETE /api/v1/me/cart/items/{id}/` *(sin PATCH: productos digitales, cantidad 1)*
- [x] Servicio `create_checkout_session()`
- [x] Endpoint `POST /api/v1/checkout/create-session/`
- [x] Credenciales Stripe vía admin `GET/PATCH /admin/site/stripe/` (como Firebase/Bunny; no en env)
- [x] Webhook `POST /api/v1/webhooks/stripe/` con verificación de firma
- [x] Handler `checkout.session.completed` → Order pagada + Purchase + AccessGrant
- [x] Idempotencia: no procesar el mismo `event.id` dos veces
- [x] Apple Pay y Google Pay en Stripe Checkout (activar en Dashboard; guía en `docs/apis/admin/site/stripe.md`)
- [x] Template email confirmación de compra (`notifications`)
- [x] Task Celery `notifications.send_purchase_confirmation`
- [x] Tests de carrito, checkout y webhook (Stripe mockeado + firma inválida)

#### Criterio de aceptación

- [x] Compra (webhook `checkout.session.completed`) otorga AccessGrant al producto
- [x] Email de confirmación de compra enviado
- [x] Webhook rechaza requests sin firma válida

**Fase completada:** ✅

---

### Fase 5 — APIs de usuario (Semana 6)

**Objetivo:** Endpoints de compras, acceso a contenido y progreso (JSON).

#### Checklist

- [x] API `GET /api/v1/me/purchases/` — listado de compras
- [x] API `GET /api/v1/me/courses/` — cursos con acceso activo y fecha expiración
- [x] API `GET /api/v1/me/recipes/` — recetas con acceso activo y fecha expiración
- [x] Modelo `LessonProgress` (usuario, lección, completada, última vista)
- [x] API `POST /api/v1/me/lessons/{id}/complete/` — marcar lección completada
- [x] API `GET /api/v1/me/progress/{course_id}/` — progreso del curso
- [x] Regla: cursos expiran a los 365 días desde compra *(grant en webhook Fase 4; listados filtran por `expires_at`)*
- [x] Regla: recetas respetan lifetime o 365 días según producto *(idem)*
- [x] Task Celery `content.expire_access_grants` — cuenta accesos vencidos (`expires_at` ya niega el video en tiempo real)
- [x] Programar job diario (cron `deploy/expire_access.cron` + `CELERY_BEAT_SCHEDULE`)
- [x] API "continuar viendo": `POST /me/lessons/{id}/view/` y `continue_lesson` en `/me/courses/` y `/me/progress/{id}/`
- [x] Tests de expiración de acceso y progreso de lecciones

#### Criterio de aceptación

- [x] APIs `/me/` devuelven productos comprados con fechas de expiración
- [x] Endpoints de contenido responden 403 tras expiración de acceso
- [x] Progreso de lecciones se persiste y se expone vía API

**Fase completada:** ✅

---

### Fase 6 — Admin y analytics (Semana 7)

**Objetivo:** APIs de dashboard financiero y gestión administrativa (JSON).

#### Checklist

- [x] Crear app `analytics`
- [x] API `GET /api/v1/admin/dashboard/` — resumen general
- [x] Métrica: ingresos totales y por período (día/semana/mes)
- [x] Métrica: ventas recientes (últimas N órdenes)
- [x] Métrica: productos más vendidos
- [x] API `GET /api/v1/admin/users/` — listado paginado *(implementado en Fase 2)*
- [x] API `GET /api/v1/admin/users/{id}/` — detalle **con historial de compras** *(detalle en Fase 2; `purchases` real en Fase 4)*
- [x] API `GET /api/v1/admin/courses/{slug}/purchases/` — listado de compras de un curso (presencial u online) *(implementado con formato de curso)*
- [x] API gestión idiomas: activar/desactivar (`/admin/languages/`) *(implementado en Fase 2)*
- [x] Documentar config Stripe (admin `/admin/site/stripe/`, toggle test/live; no env) *(implementado en Fase 4)*
- [x] Endpoint `GET /api/v1/admin/dashboard/revenue/` — serie temporal ingresos (JSON)
- [x] Tests de dashboard y endpoints admin analytics

#### Criterio de aceptación

- [x] API dashboard devuelve ingresos reales calculados desde `Order`
- [x] Admin puede ver historial de compras en detalle de usuario *(GET `/admin/users/{id}/` campo `purchases`, Fase 4)*
- [x] Estadísticas coinciden con datos de `Order` en BD

**Fase completada:** ✅

---

### Fase 7 — Despliegue y QA (Semana 8)

**Objetivo:** Producción en Digital Ocean + pruebas finales.

#### Checklist

**Infraestructura**

- [x] Desplegar Droplet Ubuntu 24.04 (Gunicorn + Nginx + Celery + Postgres + Redis locales)
- [x] Dominio `petralicious.sk` con HTTPS (Let's Encrypt / certbot)
- [x] CI/CD GitHub Actions: tests en PR/push + deploy SSH a Droplet (`deploy.yml`)
- [x] Script `deploy/remote_deploy.sh` (pip, migrate, collectstatic, restart servicios)
- [x] Documentar deploy en `docs/deploy-digitalocean.md`
- [ ] Crear `Dockerfile` production-ready *(alternativa App Platform; Droplet activo)*
- [ ] Crear `deploy/docker-entrypoint.sh` (API, worker, migrate job)
- [ ] Crear `deploy/env.digitalocean.example`
- [ ] Provisionar Managed PostgreSQL en Digital Ocean *(opcional; Postgres en Droplet)*
- [ ] Provisionar Managed Redis en Digital Ocean *(opcional; Redis en Droplet)*
- [ ] Provisionar DO Spaces para media
- [ ] Desplegar App Platform: servicio web (Gunicorn) *(alternativa; hoy Droplet)*
- [ ] Desplegar App Platform: worker Celery (componente separado)
- [x] Configurar job de migraciones en deploy (vía `remote_deploy.sh`)
- [x] Configurar dominio del cliente (`petralicious.sk`)
- [x] Verificar SSL/HTTPS activo (Let's Encrypt)

**Integraciones producción**

- [x] Variables de entorno en Droplet (`.env`: SECRET_KEY, DATABASE_URL, etc.)
- [ ] Webhook Stripe apuntando a URL pública de producción
- [ ] Stripe en modo live (o test según acuerdo con cliente)
- [x] Email transaccional producción (Mailchimp Transactional / Mandrill vía admin `/admin/site/mailchimp/`)
- [ ] Bunny.net configurado con credenciales de producción *(API admin `/admin/site/bunny/`, Fase 3)*
- [x] Mailchimp newsletter (Audience Petralicious, group Idioma, tags WEB_ES/WEB_SK)

**QA y cierre (solo API — vía pytest y requests manuales)**

- [ ] Test integración API: registro → checkout → webhook → acceso a curso/receta
- [ ] Test integración API: endpoint de video responde 200/403 según acceso
- [ ] Test integración API: admin crea curso y aparece en catálogo público
- [ ] Test integración: email confirmación de compra enviado (Celery)
- [ ] Verificar accesos expiran según reglas (curso 1 año / receta lifetime)
- [x] Publicar OpenAPI en `/api/schema/` y `/api/docs/` (Swagger/Redoc)
- [ ] Documento QA API / checklist pre-lanzamiento (sección 11) completado
- [ ] Entrega código fuente backend al cliente

#### Criterio de aceptación

- [x] API accesible en dominio vía HTTPS (`https://petralicious.sk`)
- [ ] Flujo compra vía API + Stripe sandbox funciona end-to-end
- [x] Celery worker desplegado y reiniciable vía CI/CD

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

- [ ] `SECRET_KEY` en variables de entorno (nunca en repo). Keys Stripe/Bunny/Firebase/Mailchimp solo en admin.
- [ ] `DEBUG=False` en producción
- [ ] CORS restringido a dominios del frontend externo (config only)
- [x] Webhooks Stripe verificados con signing secret *(API admin `/admin/site/stripe/`)*
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
- Guía de integraciones (Firebase, Bunny, Stripe, Mailchimp, Google): [`docs/configurar-integraciones.md`](./configurar-integraciones.md)
- Newsletter frontend: [`docs/frontend-newsletter.md`](./frontend-newsletter.md)
- [Stripe Checkout](https://stripe.com/docs/checkout)
