from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.commerce.api.admin.views import AdminPaymentAttemptViewSet

router = DefaultRouter()
router.register("payments", AdminPaymentAttemptViewSet, basename="admin-payments")

urlpatterns = [
    path("", include(router.urls)),
]
