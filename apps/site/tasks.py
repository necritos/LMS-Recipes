import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="site.sync_newsletter_mailchimp",
    max_retries=3,
    default_retry_delay=60,
)
def sync_newsletter_to_mailchimp_task(self, subscriber_id: str) -> dict:
    from apps.site.models import NewsletterSubscriber
    from apps.site.services.mailchimp_service import upsert_newsletter_member

    subscriber = NewsletterSubscriber.objects.filter(pk=subscriber_id).first()
    if subscriber is None:
        return {"ok": False, "reason": "missing"}
    try:
        updated = upsert_newsletter_member(subscriber=subscriber)
    except Exception as exc:
        logger.warning("Mailchimp sync retry for %s: %s", subscriber_id, exc)
        raise self.retry(exc=exc) from exc
    return {
        "ok": updated.mailchimp_status == NewsletterSubscriber.MailchimpStatus.SYNCED,
        "status": updated.mailchimp_status,
    }
