from django.db import transaction
from django.utils import timezone

from apps.common.exceptions import BusinessError
from apps.site.constants import MAX_EXTRA_TAGS, NEWSLETTER_LANGUAGES
from apps.site.models import ContactMessage, NewsletterSubscriber
from apps.site.services.mailchimp_service import (
    dispatch_mailchimp_sync,
    marketing_configured,
    normalize_extra_tags,
)


@transaction.atomic
def create_contact_message(
    *,
    name: str,
    email: str,
    topic: str,
    message: str,
) -> ContactMessage:
    return ContactMessage.objects.create(
        name=name.strip(),
        email=email.strip().lower(),
        topic=topic.strip(),
        message=message.strip(),
    )


@transaction.atomic
def set_contact_read(*, message: ContactMessage, is_read: bool) -> ContactMessage:
    message.is_read = is_read
    message.save(update_fields=["is_read", "updated_at"])
    return message


@transaction.atomic
def subscribe_newsletter(
    *,
    email: str,
    name: str,
    language: str,
    consent: bool,
    tags: list[str] | None = None,
) -> NewsletterSubscriber:
    if not consent:
        raise BusinessError(
            "CONSENT_REQUIRED",
            "Debes aceptar recibir comunicaciones comerciales / newsletter.",
            http_status=422,
        )
    lang = (language or "").strip().lower()
    if lang not in NEWSLETTER_LANGUAGES:
        raise BusinessError(
            "NEWSLETTER_LANGUAGE_INVALID",
            "El idioma debe ser 'es' (web ES) o 'sk' (web SK).",
            http_status=422,
        )
    extra_tags = normalize_extra_tags(tags)
    if len(extra_tags) > MAX_EXTRA_TAGS:
        raise BusinessError(
            "NEWSLETTER_TAGS_LIMIT",
            f"Puedes enviar como máximo {MAX_EXTRA_TAGS} tags extra.",
            http_status=422,
        )

    normalized = email.strip().lower()
    display_name = (name or "").strip()
    if not display_name:
        raise BusinessError(
            "NEWSLETTER_NAME_REQUIRED",
            "El nombre es obligatorio.",
            http_status=422,
        )
    if NewsletterSubscriber.objects.filter(email=normalized).exists():
        raise BusinessError(
            "EMAIL_ALREADY_SUBSCRIBED",
            "Este email ya está suscrito al newsletter.",
            http_status=409,
        )

    now = timezone.now()
    mailchimp_on = marketing_configured()
    subscriber = NewsletterSubscriber.objects.create(
        email=normalized,
        name=display_name,
        language=lang,
        consent=True,
        consented_at=now,
        extra_tags=extra_tags,
        mailchimp_status=(
            NewsletterSubscriber.MailchimpStatus.PENDING
            if mailchimp_on
            else NewsletterSubscriber.MailchimpStatus.SKIPPED
        ),
    )
    if mailchimp_on:
        transaction.on_commit(
            lambda sid=str(subscriber.id): dispatch_mailchimp_sync(subscriber_id=sid)
        )
    return subscriber
