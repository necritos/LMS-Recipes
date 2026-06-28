from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from apps.accounts.models import UserAccount, UserAccountStatus
from apps.accounts.selectors import get_user_account_by_email, get_user_account_by_google_id
from apps.common.exceptions import BusinessError
from apps.notifications.tasks import send_welcome_email_task


def _verify_google_id_token(*, token: str) -> dict:
    if not settings.GOOGLE_CLIENT_ID:
        raise BusinessError(
            "GOOGLE_NOT_CONFIGURED",
            "Google OAuth no está configurado en el servidor.",
            http_status=503,
        )
    try:
        return id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError as exc:
        raise BusinessError(
            "INVALID_GOOGLE_TOKEN",
            "El token de Google no es válido.",
            http_status=401,
        ) from exc


@transaction.atomic
def login_or_register_with_google(*, id_token_value: str) -> tuple[UserAccount, bool]:
    payload = _verify_google_id_token(token=id_token_value)
    google_id = payload.get("sub")
    email = (payload.get("email") or "").strip().lower()
    if not google_id or not email:
        raise BusinessError(
            "INVALID_GOOGLE_TOKEN",
            "El token de Google no incluye email o identificador.",
            http_status=401,
        )
    if not payload.get("email_verified"):
        raise BusinessError(
            "EMAIL_NOT_VERIFIED",
            "El email de Google no está verificado.",
            http_status=422,
        )

    created = False
    user_account = get_user_account_by_google_id(google_id)
    if user_account is None:
        user_account = get_user_account_by_email(email)
        if user_account is None:
            user_account = UserAccount.objects.create(
                email=email,
                password=make_password(None),
                google_id=google_id,
                first_name=payload.get("given_name", "") or "",
                last_name=payload.get("family_name", "") or "",
                status=UserAccountStatus.ACTIVE,
                email_verified_at=timezone.now(),
            )
            created = True
            transaction.on_commit(
                lambda uid=str(user_account.id): send_welcome_email_task.delay(uid)
            )
        elif user_account.google_id is None:
            user_account.google_id = google_id
            user_account.email_verified_at = user_account.email_verified_at or timezone.now()
            user_account.save(update_fields=["google_id", "email_verified_at", "updated_at"])

    if user_account.status == UserAccountStatus.SUSPENDED:
        raise BusinessError(
            "ACCOUNT_SUSPENDED",
            "La cuenta está suspendida.",
            http_status=403,
        )

    user_account.last_login = timezone.now()
    user_account.save(update_fields=["last_login", "updated_at"])
    return user_account, created
