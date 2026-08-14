import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="content.expire_access_grants")
def expire_access_grants_task() -> dict:
    from apps.content.services.expiry_service import expire_access_grants

    result = expire_access_grants()
    logger.info("Access grants vencidos: %s", result["expired_count"])
    return result
