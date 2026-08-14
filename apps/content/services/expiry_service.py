from django.utils import timezone

from apps.content.models import AccessGrant


def expire_access_grants() -> dict:
    """Cuenta grants temporales ya vencidos. El 403 en video usa `expires_at` en tiempo real."""
    now = timezone.now()
    expired_count = AccessGrant.objects.filter(
        is_revoked=False,
        expires_at__isnull=False,
        expires_at__lte=now,
    ).count()
    return {"expired_count": expired_count}
