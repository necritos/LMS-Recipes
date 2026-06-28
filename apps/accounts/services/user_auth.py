from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserAccount, UserAccountStatus
from apps.accounts.selectors import get_user_account_by_email
from apps.common.exceptions import BusinessError


def _validate_password_pair(*, password: str, password_confirm: str) -> None:
    if password != password_confirm:
        raise BusinessError(
            "PASSWORD_MISMATCH",
            "Las contraseñas no coinciden.",
            http_status=422,
        )
    if len(password) < 8:
        raise BusinessError(
            "WEAK_PASSWORD",
            "La contraseña debe tener al menos 8 caracteres.",
            http_status=422,
        )


@transaction.atomic
def register_user(
    *,
    email: str,
    password: str,
    password_confirm: str,
    first_name: str = "",
    last_name: str = "",
    terms_accepted: bool,
) -> UserAccount:
    if not terms_accepted:
        raise BusinessError(
            "TERMS_NOT_ACCEPTED",
            "Debes aceptar los términos y condiciones.",
            http_status=422,
        )

    _validate_password_pair(password=password, password_confirm=password_confirm)

    email = email.strip().lower()
    if get_user_account_by_email(email):
        raise BusinessError(
            "EMAIL_ALREADY_REGISTERED",
            "Ya existe una cuenta con este email.",
            http_status=409,
        )

    user_account = UserAccount.objects.create(
        email=email,
        password=make_password(password),
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        status=UserAccountStatus.ACTIVE,
    )

    from apps.notifications.tasks import send_welcome_email_task

    transaction.on_commit(lambda uid=str(user_account.id): send_welcome_email_task.delay(uid))
    return user_account


@transaction.atomic
def login_user(*, email: str, password: str) -> UserAccount:
    from django.contrib.auth.hashers import check_password

    user_account = get_user_account_by_email(email)
    if user_account is None or not check_password(password, user_account.password):
        raise BusinessError(
            "INVALID_CREDENTIALS",
            "Email o contraseña incorrectos.",
            http_status=401,
        )
    if user_account.status == UserAccountStatus.SUSPENDED:
        raise BusinessError(
            "ACCOUNT_SUSPENDED",
            "La cuenta está suspendida.",
            http_status=403,
        )
    user_account.last_login = timezone.now()
    user_account.save(update_fields=["last_login", "updated_at"])
    return user_account
