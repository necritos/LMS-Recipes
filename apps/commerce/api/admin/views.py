from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets

from apps.commerce.api.admin.serializers import AdminPaymentAttemptSerializer
from apps.commerce.models import PaymentAttempt
from apps.commerce.selectors import payment_attempts_for_admin
from apps.common.permissions import IsStaffUser


@extend_schema_view(
    list=extend_schema(
        tags=["Admin — Payments"],
        parameters=[
            OpenApiParameter(
                "outcome",
                str,
                description="started | succeeded | failed | expired",
            ),
            OpenApiParameter("search", str, description="Email, nombre o id de Stripe"),
            OpenApiParameter("page", int),
            OpenApiParameter("page_size", int),
        ],
    ),
    retrieve=extend_schema(tags=["Admin — Payments"]),
)
class AdminPaymentAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsStaffUser]
    serializer_class = AdminPaymentAttemptSerializer
    queryset = PaymentAttempt.objects.none()

    def get_queryset(self):
        outcome = self.request.query_params.get("outcome", "").strip()
        search = self.request.query_params.get("search", "").strip()
        return payment_attempts_for_admin(outcome=outcome or None, search=search)
