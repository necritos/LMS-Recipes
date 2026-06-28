from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import transaction

from apps.accounts.constants import OtpPurpose
from apps.accounts.models import UserAccount, UserAccountStatus
from apps.accounts.selectors import get_user_account_by_email
from apps.accounts.services.otp_code import issue_otp_code, validate_otp_code
from apps.accounts.services.user_auth import _validate_password_pair
from apps.common.exceptions import BusinessError
from apps.notifications.services.mail import dispatch_transactional_email


def _get_user_for_password_reset(*, email: str) -> UserAccount | None:
    user_account = get_user_account_by_email(email)
    if user_account is None:
        return None
    if user_account.status == UserAccountStatus.SUSPENDED:
        return None
    return user_account


def _send_password_reset_code(*, user_account: UserAccount) -> None:
    code = issue_otp_code(user_account=user_account, purpose=OtpPurpose.PASSWORD_RESET)
    dispatch_transactional_email(
        to=user_account.email,
        subject=f"{settings.SITE_NAME} — recupera tu contraseña",
        template_name="notifications/emails/password_reset.html",
        context={
            "site_name": settings.SITE_NAME,
            "code": code,
            "user_name": user_account.first_name or user_account.email,
        },
        require_mail=False,
    )


def request_password_reset(*, email: str) -> None:
    user_account = _get_user_for_password_reset(email=email)
    if user_account is not None:
        _send_password_reset_code(user_account=user_account)


def verify_password_reset_code(*, email: str, code: str) -> None:
    user_account = _get_user_for_password_reset(email=email)
    if user_account is None:
        raise BusinessError(
            "INVALID_CODE",
            "El código no es válido.",
            http_status=422,
        )
    validate_otp_code(
        user_account=user_account,
        purpose=OtpPurpose.PASSWORD_RESET,
        code=code,
        consume=False,
    )


@transaction.atomic
def reset_password_with_code(
    *,
    email: str,
    code: str,
    password: str,
    password_confirm: str,
) -> None:
    _validate_password_pair(password=password, password_confirm=password_confirm)

    user_account = _get_user_for_password_reset(email=email)
    if user_account is None:
        raise BusinessError(
            "INVALID_CODE",
            "El código no es válido.",
            http_status=422,
        )

    validate_otp_code(
        user_account=user_account,
        purpose=OtpPurpose.PASSWORD_RESET,
        code=code,
        consume=True,
    )
    user_account.password = make_password(password)
    user_account.save(update_fields=["password", "updated_at"])
