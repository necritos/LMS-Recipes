from datetime import datetime, timedelta

from django.utils import timezone

from apps.catalog.constants import RecipeAccessType
from apps.content.models import AccessGrant


def expires_at_for_order_item(item) -> datetime | None:
    if item.is_lifetime or item.access_days is None:
        return None
    return timezone.now() + timedelta(days=item.access_days)


def upsert_access_grant(*, user, item) -> AccessGrant:
    lookup: dict = {"user": user}
    if item.course_id:
        lookup["course"] = item.course
    else:
        lookup["recipe"] = item.recipe

    new_expires = expires_at_for_order_item(item)
    grant = AccessGrant.objects.filter(**lookup).first()
    if grant is None:
        return AccessGrant.objects.create(
            **lookup,
            expires_at=new_expires,
            is_revoked=False,
            source=AccessGrant.Source.PURCHASE,
        )

    if grant.expires_at is None or new_expires is None:
        grant.expires_at = None
    else:
        grant.expires_at = max(grant.expires_at, new_expires)
    grant.is_revoked = False
    grant.source = AccessGrant.Source.PURCHASE
    grant.save(update_fields=["expires_at", "is_revoked", "source", "updated_at"])
    return grant


def snapshot_access(*, course=None, recipe=None) -> tuple[int | None, bool]:
    if course is not None:
        return course.access_days, False
    if recipe.access_type == RecipeAccessType.LIFETIME:
        return None, True
    return recipe.access_days, False
