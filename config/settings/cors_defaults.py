"""Orígenes CORS/CSRF de producción (wildcards).

django-cors-headers no admite `*` en CORS_ALLOWED_ORIGINS; usamos regexes.
Django CSRF sí admite `https://*.dominio` y apex explícito.
"""

PRODUCTION_CORS_ORIGIN_REGEXES = [
    r"^https://[\w-]+\.web\.app$",
    r"^https://([\w-]+\.)?petralicious\.com$",
    r"^https://([\w-]+\.)?petralicious\.sk$",
]

PRODUCTION_CSRF_TRUSTED_ORIGINS = [
    "https://*.web.app",
    "https://petralicious.com",
    "https://*.petralicious.com",
    "https://petralicious.sk",
    "https://*.petralicious.sk",
]
