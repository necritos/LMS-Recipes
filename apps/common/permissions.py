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


class HasActiveAccess(BasePermission):
    """Usuario final + AccessGrant activo. La vista define get_access_target()."""

    def has_permission(self, request, view):
        if not (
            isinstance(request.user, UserAccount)
            and request.user.status != UserAccountStatus.SUSPENDED
        ):
            return False
        if not hasattr(view, "get_access_target"):
            return True
        from apps.content.services.access_service import require_active_access

        require_active_access(user=request.user, **view.get_access_target())
        return True
