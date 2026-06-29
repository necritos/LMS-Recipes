from django.db.models import Q, QuerySet

from apps.accounts.models import UserAccount


def get_user_account_by_email(email: str) -> UserAccount | None:
    normalized = email.strip().lower()
    if not normalized:
        return None
    return UserAccount.objects.filter(email=normalized).first()


def get_user_account_by_google_id(google_id: str) -> UserAccount | None:
    if not google_id:
        return None
    return UserAccount.objects.filter(google_id=google_id).first()


def list_user_accounts_for_admin(
    *,
    search: str = "",
    status: str | None = None,
) -> QuerySet[UserAccount]:
    qs = UserAccount.objects.all()
    if search:
        qs = qs.filter(
            Q(email__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
        )
    if status:
        qs = qs.filter(status=status)
    return qs.order_by("-created_at")
