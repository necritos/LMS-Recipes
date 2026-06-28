from django.urls import path

from apps.accounts.api.admin.auth_views import AdminLoginView, AdminLogoutView

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin-auth-login"),
    path("logout/", AdminLogoutView.as_view(), name="admin-auth-logout"),
]
