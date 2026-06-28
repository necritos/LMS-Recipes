import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.accounts.constants import (
    OTP_CODE_LENGTH,
    OTP_CODE_TTL_MINUTES,
    OTP_MAX_ATTEMPTS,
    OTP_RESEND_COOLDOWN_SECONDS,
)
from apps.accounts.models import UserAccount, UserAccountOtpCode
from apps.common.exceptions import BusinessError


def _hash_code(*, user_account_id, code: str) -> str:
    payload = f"{user_account_id}:{code}:{settings.SECRET_KEY}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def generate_six_digit_code() -> str:
    return f"{secrets.randbelow(10**OTP_CODE_LENGTH):0{OTP_CODE_LENGTH}d}"


def _get_latest_code(*, user_account: UserAccount, purpose: str) -> UserAccountOtpCode | None:
    return (
        UserAccountOtpCode.objects.filter(
            user_account=user_account,
            purpose=purpose,
            consumed_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )


def assert_resend_allowed(*, user_account: UserAccount, purpose: str) -> None:
    latest = (
        UserAccountOtpCode.objects.filter(user_account=user_account, purpose=purpose)
        .order_by("-created_at")
        .first()
    )
    if latest is None:
        return
    elapsed = (timezone.now() - latest.created_at).total_seconds()
    if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
        raise BusinessError(
            "RESEND_TOO_SOON",
            "Debes esperar antes de solicitar un nuevo código.",
            http_status=429,
            details={"retry_after_seconds": int(OTP_RESEND_COOLDOWN_SECONDS - elapsed)},
        )


@transaction.atomic
def issue_otp_code(*, user_account: UserAccount, purpose: str) -> str:
    assert_resend_allowed(user_account=user_account, purpose=purpose)

    plain_code = generate_six_digit_code()
    now = timezone.now()
    UserAccountOtpCode.objects.filter(
        user_account=user_account,
        purpose=purpose,
        consumed_at__isnull=True,
    ).update(consumed_at=now)

    UserAccountOtpCode.objects.create(
        user_account=user_account,
        purpose=purpose,
        code_hash=_hash_code(user_account_id=user_account.id, code=plain_code),
        expires_at=now + timedelta(minutes=OTP_CODE_TTL_MINUTES),
    )
    return plain_code


def _get_active_code(*, user_account: UserAccount, purpose: str) -> UserAccountOtpCode:
    otp = _get_latest_code(user_account=user_account, purpose=purpose)
    if otp is None:
        raise BusinessError(
            "CODE_NOT_FOUND",
            "No hay un código activo. Solicita uno nuevo.",
            http_status=422,
        )
    if otp.consumed_at is not None:
        raise BusinessError(
            "CODE_ALREADY_USED",
            "Este código ya fue utilizado.",
            http_status=422,
        )
    if otp.expires_at <= timezone.now():
        raise BusinessError(
            "CODE_EXPIRED",
            "El código expiró. Solicita uno nuevo.",
            http_status=422,
        )
    if otp.failed_attempts >= OTP_MAX_ATTEMPTS:
        raise BusinessError(
            "CODE_MAX_ATTEMPTS",
            "Superaste los intentos permitidos. Solicita un nuevo código.",
            http_status=422,
        )
    return otp


@transaction.atomic
def validate_otp_code(
    *,
    user_account: UserAccount,
    purpose: str,
    code: str,
    consume: bool = False,
) -> UserAccountOtpCode:
    normalized = (code or "").strip()
    if len(normalized) != OTP_CODE_LENGTH or not normalized.isdigit():
        raise BusinessError(
            "INVALID_CODE",
            "El código debe tener 6 dígitos.",
            http_status=422,
        )

    otp = _get_active_code(user_account=user_account, purpose=purpose)
    expected = _hash_code(user_account_id=user_account.id, code=normalized)
    if otp.code_hash != expected:
        otp.failed_attempts += 1
        otp.save(update_fields=["failed_attempts", "updated_at"])
        raise BusinessError(
            "INVALID_CODE",
            "El código no es válido.",
            http_status=422,
        )

    if consume:
        otp.consumed_at = timezone.now()
        otp.save(update_fields=["consumed_at", "updated_at"])
    return otp
