from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets

from apps.accounts.api.admin.user_serializers import (
    AdminUserAccountDetailSerializer,
    AdminUserAccountSerializer,
)
from apps.accounts.models import UserAccount
from apps.accounts.selectors import list_user_accounts_for_admin
from apps.common.permissions import IsStaffUser


@extend_schema_view(
    list=extend_schema(
        tags=["Admin — Users"],
        parameters=[
            OpenApiParameter("search", str, description="Buscar por email o nombre"),
            OpenApiParameter(
                "status",
                str,
                description="Filtrar por estado: active | suspended",
            ),
            OpenApiParameter("page", int, description="Número de página"),
            OpenApiParameter("page_size", int, description="Tamaño de página (máx. 100)"),
        ],
    ),
    retrieve=extend_schema(tags=["Admin — Users"]),
)
class AdminUserAccountViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsStaffUser]
    lookup_field = "pk"
    queryset = UserAccount.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AdminUserAccountDetailSerializer
        return AdminUserAccountSerializer

    def get_queryset(self):
        search = self.request.query_params.get("search", "").strip()
        status = self.request.query_params.get("status", "").strip()
        return list_user_accounts_for_admin(search=search, status=status or None)
