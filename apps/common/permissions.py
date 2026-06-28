from rest_framework.permissions import BasePermission

from apps.accounts.models import StaffUser, UserAccount, UserAccountStatus


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, StaffUser) and request.user.is_active


class IsAuthenticatedUser(BasePermission):
    def has_permission(self, request, view):
        return (
            isinstance(request.user, UserAccount)
            and request.user.status != UserAccountStatus.SUSPENDED
        )
