from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string

from apps.common.exceptions import BusinessError


def is_mail_configured() -> bool:
    backend = settings.EMAIL_BACKEND
    if "console" in backend or "locmem" in backend:
        return True
    return bool(settings.EMAIL_HOST and settings.DEFAULT_FROM_EMAIL)


def send_email(
    *,
    to: str,
    subject: str,
    text: str,
    html: str | None = None,
    from_email: str | None = None,
) -> dict:
    sender = from_email or settings.DEFAULT_FROM_EMAIL
    message = EmailMultiAlternatives(subject=subject, body=text, from_email=sender, to=[to])
    if html:
        message.attach_alternative(html, "text/html")
    message.send(fail_silently=False)
    return {"to": to, "subject": subject}


def send_templated_email(
    *,
    to: str,
    subject: str,
    template_name: str,
    context: dict,
    from_email: str | None = None,
) -> dict:
    html = render_to_string(template_name, context)
    text = render_to_string(template_name.replace(".html", ".txt"), context)
    return send_email(to=to, subject=subject, text=text, html=html, from_email=from_email)


def _enqueue_send_email(**kwargs) -> None:
    from apps.notifications.tasks import send_email_task

    transaction.on_commit(lambda: send_email_task.delay(**kwargs))


def dispatch_transactional_email(
    *,
    to: str,
    subject: str,
    template_name: str | None = None,
    context: dict | None = None,
    text: str | None = None,
    html: str | None = None,
    require_mail: bool = True,
) -> None:
    if not is_mail_configured():
        if require_mail:
            raise BusinessError(
                "MAIL_DISABLED",
                "El envío de correo no está habilitado.",
                http_status=422,
            )
        return

    payload = {
        "to": to,
        "subject": subject,
        "template_name": template_name,
        "context": context or {},
        "text": text,
        "html": html,
    }

    if settings.MAIL_ASYNC:
        _enqueue_send_email(**payload)
        return

    if template_name:
        send_templated_email(
            to=to,
            subject=subject,
            template_name=template_name,
            context=context or {},
        )
        return
    send_email(to=to, subject=subject, text=text or "", html=html)
