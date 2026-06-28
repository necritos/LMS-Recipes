from django.contrib import admin

from apps.accounts.models import StaffUser, UserAccount, UserAccountOtpCode


@admin.register(StaffUser)
class StaffUserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "is_active", "is_superuser")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ("email", "status", "google_id", "last_login", "created_at")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


@admin.register(UserAccountOtpCode)
class UserAccountOtpCodeAdmin(admin.ModelAdmin):
    list_display = ("user_account", "purpose", "expires_at", "consumed_at", "failed_attempts")
    list_filter = ("purpose",)
    ordering = ("-created_at",)
