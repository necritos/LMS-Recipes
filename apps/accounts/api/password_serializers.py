from rest_framework import serializers

from apps.accounts.services.password_reset import (
    request_password_reset,
    reset_password_with_code,
    verify_password_reset_code,
)


class PasswordForgotSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        request_password_reset(email=validated_data["email"])
        return validated_data


class PasswordVerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def create(self, validated_data):
        verify_password_reset_code(
            email=validated_data["email"],
            code=validated_data["code"],
        )
        return validated_data


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def create(self, validated_data):
        reset_password_with_code(**validated_data)
        return validated_data
