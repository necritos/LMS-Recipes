import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="notifications.send_email",
    max_retries=3,
    default_retry_delay=60,
)
def send_email_task(
    self,
    *,
    to: str,
    subject: str,
    template_name: str | None = None,
    context: dict | None = None,
    text: str | None = None,
    html: str | None = None,
) -> dict:
    from apps.notifications.services.mail import send_email, send_templated_email

    try:
        if template_name:
            result = send_templated_email(
                to=to,
                subject=subject,
                template_name=template_name,
                context=context or {},
            )
        else:
            result = send_email(to=to, subject=subject, text=text or "", html=html)
        logger.info("Email enviado vía Celery a %s", result.get("to"))
        return result
    except Exception as exc:
        logger.warning("Fallo envío email, reintento Celery: %s", exc)
        raise self.retry(exc=exc) from exc


@shared_task(name="notifications.send_welcome_email")
def send_welcome_email_task(user_account_id: str) -> dict:
    from django.conf import settings

    from apps.accounts.models import UserAccount
    from apps.notifications.services.mail import send_templated_email

    user_account = UserAccount.objects.get(pk=user_account_id)
    return send_templated_email(
        to=user_account.email,
        subject=f"Bienvenido/a a {settings.SITE_NAME}",
        template_name="notifications/emails/welcome.html",
        context={
            "site_name": settings.SITE_NAME,
            "user_name": user_account.first_name or user_account.email,
        },
    )
