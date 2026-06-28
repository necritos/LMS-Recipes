from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserAccount


class StaffRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token["type"] = "staff"
        return token


class UserRefreshToken(RefreshToken):
    @classmethod
    def for_user_account(cls, user_account: UserAccount):
        token = cls()
        token["sub"] = str(user_account.id)
        token["user_id"] = str(user_account.id)
        token["type"] = "user"
        return token


class StaffTokenObtainPairSerializer(TokenObtainPairSerializer):
    token_class = StaffRefreshToken

    @classmethod
    def get_token(cls, user):
        return StaffRefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data["user"] = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        return data
