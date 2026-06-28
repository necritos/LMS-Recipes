from rest_framework import serializers

from apps.accounts.jwt import StaffTokenObtainPairSerializer


class AdminLoginSerializer(StaffTokenObtainPairSerializer):
    pass


class AdminLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
