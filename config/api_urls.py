from django.urls import include, path

urlpatterns = [
    path("", include("apps.common.api.urls")),
    path("auth/", include("apps.accounts.api.auth_urls")),
    path("admin/auth/", include("apps.accounts.api.admin.auth_urls")),
]
