from django.db import transaction

from apps.common.exceptions import BusinessError
from apps.site.models import ContactMessage, NewsletterSubscriber


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
def subscribe_newsletter(*, email: str) -> NewsletterSubscriber:
    normalized = email.strip().lower()
    if NewsletterSubscriber.objects.filter(email=normalized).exists():
        raise BusinessError(
            "EMAIL_ALREADY_SUBSCRIBED",
            "Este email ya está suscrito al newsletter.",
            http_status=409,
        )
    return NewsletterSubscriber.objects.create(email=normalized)
