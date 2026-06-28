from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.api.auth_serializers import (
    GoogleAuthSerializer,
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
)
from apps.accounts.api.password_serializers import (
    PasswordForgotSerializer,
    PasswordResetSerializer,
    PasswordVerifyCodeSerializer,
)
from apps.accounts.jwt import UserRefreshToken
from apps.accounts.services.google_auth import login_or_register_with_google
from apps.accounts.services.user_auth import login_user
from apps.common.permissions import IsAuthenticatedUser


@extend_schema(tags=["Auth"])
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_account = serializer.save()
        refresh = UserRefreshToken.for_user_account(user_account)
        return Response(
            {
                "data": {
                    "id": str(user_account.id),
                    "email": user_account.email,
                    "first_name": user_account.first_name,
                    "last_name": user_account.last_name,
                    "status": user_account.status,
                    "email_verified": user_account.email_verified_at is not None,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "meta": {},
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Auth"])
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_account = login_user(**serializer.validated_data)
        refresh = UserRefreshToken.for_user_account(user_account)
        return Response(
            {
                "data": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": str(user_account.id),
                        "email": user_account.email,
                        "first_name": user_account.first_name,
                        "last_name": user_account.last_name,
                        "status": user_account.status,
                        "email_verified": user_account.email_verified_at is not None,
                    },
                },
                "meta": {},
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["Auth"])
class LogoutView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
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


@extend_schema(tags=["Auth"])
class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_account, created = login_or_register_with_google(
            id_token_value=serializer.validated_data["id_token"],
        )
        refresh = UserRefreshToken.for_user_account(user_account)
        return Response(
            {
                "data": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "created": created,
                    "user": {
                        "id": str(user_account.id),
                        "email": user_account.email,
                        "first_name": user_account.first_name,
                        "last_name": user_account.last_name,
                        "status": user_account.status,
                        "email_verified": user_account.email_verified_at is not None,
                    },
                },
                "meta": {},
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


@extend_schema(tags=["Auth"])
class PasswordForgotView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordForgotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "data": {
                    "message": (
                        "Si el correo está registrado, recibirás un código para "
                        "restablecer tu contraseña."
                    ),
                },
                "meta": {},
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["Auth"])
class PasswordVerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordVerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"data": {"valid": True}, "meta": {}}, status=status.HTTP_200_OK)


@extend_schema(tags=["Auth"])
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"data": {"message": "Contraseña actualizada correctamente."}, "meta": {}},
            status=status.HTTP_200_OK,
        )
