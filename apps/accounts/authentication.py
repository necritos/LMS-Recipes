from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from apps.accounts.models import UserAccount, UserAccountStatus


class RecetarioJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        token_type = validated_token.get("type")
        if token_type == "user":
            return self._get_user_account(validated_token)
        return super().get_user(validated_token)

    def _get_user_account(self, validated_token):
        user_id = validated_token.get("user_id") or validated_token.get("sub")
        if not user_id:
            raise InvalidToken("Token sin identificador de usuario.")
        try:
            user_account = UserAccount.objects.get(pk=user_id)
        except UserAccount.DoesNotExist as exc:
            raise InvalidToken("Usuario no encontrado.") from exc
        if user_account.status == UserAccountStatus.SUSPENDED:
            raise InvalidToken("Cuenta suspendida.")
        return user_account
