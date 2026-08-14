from django.utils import timezone

from apps.catalog.models import Course, Recipe
from apps.common.exceptions import BusinessError
from apps.content.models import AccessGrant


def require_active_access(*, user, course: Course | None = None, recipe: Recipe | None = None):
    if course is None and recipe is None:
        raise ValueError("Debes indicar course o recipe.")
    qs = AccessGrant.objects.filter(user=user)
    if course is not None:
        qs = qs.filter(course=course)
    else:
        qs = qs.filter(recipe=recipe)
    grant = qs.first()
    if grant is None or grant.is_revoked:
        raise BusinessError(
            "ACCESS_DENIED",
            "No tienes acceso a este contenido.",
            http_status=403,
        )
    if grant.expires_at is not None and grant.expires_at <= timezone.now():
        raise BusinessError(
            "ACCESS_EXPIRED",
            "Tu acceso ha expirado.",
            http_status=403,
        )
    return grant
