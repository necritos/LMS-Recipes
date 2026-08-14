from django.urls import include, path

urlpatterns = [
    path("", include("apps.common.api.urls")),
    path("public/", include("apps.catalog.api.public.urls")),
    path("public/", include("apps.site.api.public.urls")),
    path("auth/", include("apps.accounts.api.auth_urls")),
    path("admin/auth/", include("apps.accounts.api.admin.auth_urls")),
    path("admin/", include("apps.accounts.api.admin.urls")),
    path("admin/", include("apps.catalog.api.admin.urls")),
    path("admin/", include("apps.site.api.admin.urls")),
    path("admin/", include("apps.content.api.admin.urls")),
    path("me/", include("apps.content.api.me.urls")),
    path("me/", include("apps.commerce.api.me.urls")),
    path("checkout/", include("apps.commerce.api.checkout.urls")),
    path("webhooks/", include("apps.commerce.api.webhooks.urls")),
]
