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
