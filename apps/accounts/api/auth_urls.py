from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.api.auth_views import (
    GoogleAuthView,
    LoginView,
    LogoutView,
    PasswordForgotView,
    PasswordResetView,
    PasswordVerifyCodeView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("google/", GoogleAuthView.as_view(), name="auth-google"),
    path("password/forgot/", PasswordForgotView.as_view(), name="auth-password-forgot"),
    path(
        "password/verify-code/",
        PasswordVerifyCodeView.as_view(),
        name="auth-password-verify-code",
    ),
    path("password/reset/", PasswordResetView.as_view(), name="auth-password-reset"),
]
