from django.conf import settings as django_settings

from apps.site.selectors import get_site_settings


def resolve_google_client_id() -> str:
    """Client ID desde admin (si OAuth está activo) o fallback `GOOGLE_CLIENT_ID` en env."""
    site = get_site_settings()
    if site.google_oauth_enabled:
        return (site.google_client_id or "").strip()
    return (django_settings.GOOGLE_CLIENT_ID or "").strip()


def google_oauth_public_config() -> dict:
    """Payload seguro para el frontend (Client ID es público por diseño de Google)."""
    client_id = resolve_google_client_id()
    enabled = bool(client_id)
    return {
        "enabled": enabled,
        "client_id": client_id if enabled else "",
    }
