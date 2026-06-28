from django.db import models


class OtpPurpose(models.TextChoices):
    PASSWORD_RESET = "password_reset", "Recuperación de contraseña"


OTP_CODE_LENGTH = 6
OTP_CODE_TTL_MINUTES = 15
OTP_MAX_ATTEMPTS = 5
OTP_RESEND_COOLDOWN_SECONDS = 60
