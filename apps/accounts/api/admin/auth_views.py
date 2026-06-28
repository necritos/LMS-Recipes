from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.api.admin.auth_serializers import AdminLoginSerializer, AdminLogoutSerializer
from apps.common.permissions import IsStaffUser


@extend_schema(tags=["Admin — Auth"])
class AdminLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = AdminLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data
        return Response(
            {
                "data": {
                    "access": tokens["access"],
                    "refresh": tokens["refresh"],
                    "user": tokens["user"],
                },
                "meta": {},
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["Admin — Auth"])
class AdminLogoutView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request):
        serializer = AdminLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            return Response(
                {
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "El token de refresco no es válido.",
                        "details": None,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"data": {"message": "Sesión cerrada correctamente."}, "meta": {}},
            status=status.HTTP_200_OK,
        )
