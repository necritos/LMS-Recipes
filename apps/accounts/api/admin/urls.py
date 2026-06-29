from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.api.admin.user_views import AdminUserAccountViewSet

router = DefaultRouter()
router.register("users", AdminUserAccountViewSet, basename="admin-users")

urlpatterns = [
    path("", include(router.urls)),
]
