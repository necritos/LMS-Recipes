from django.urls import include, path

urlpatterns = [
    path("", include("apps.common.api.urls")),
    path("public/", include("apps.catalog.api.public.urls")),
    path("auth/", include("apps.accounts.api.auth_urls")),
    path("admin/auth/", include("apps.accounts.api.admin.auth_urls")),
    path("admin/", include("apps.accounts.api.admin.urls")),
    path("admin/", include("apps.catalog.api.admin.urls")),
]
