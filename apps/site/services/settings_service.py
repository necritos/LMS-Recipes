import json

from django.db import transaction

from apps.common.exceptions import BusinessError
from apps.common.storage import invalidate_media_storage_cache
from apps.site.models import SiteSettings
from apps.site.selectors import get_site_settings
from apps.site.services.i18n import upsert_settings_translations


def _validate_firebase_payload(*, enabled: bool, project_id: str, bucket: str, credentials: str):
    if not enabled:
        return
    if not project_id.strip() or not bucket.strip() or not credentials.strip():
        raise BusinessError(
            "FIREBASE_CONFIG_INCOMPLETE",
            "Para activar Firebase Storage necesitas project_id, bucket y credentials JSON.",
            http_status=422,
        )
    try:
        payload = json.loads(credentials)
    except json.JSONDecodeError as exc:
        raise BusinessError(
            "FIREBASE_CREDENTIALS_INVALID",
            "El JSON de credenciales de Firebase no es válido.",
            http_status=422,
        ) from exc
    if not isinstance(payload, dict) or payload.get("type") != "service_account":
        raise BusinessError(
            "FIREBASE_CREDENTIALS_INVALID",
            "Las credenciales deben ser un JSON de service account de Firebase.",
            http_status=422,
        )


@transaction.atomic
def update_site_settings(*, fields: dict) -> SiteSettings:
    settings = get_site_settings()
    credentials = fields.get("firebase_credentials_json", None)
    if credentials == "":
        credentials = settings.firebase_credentials_json
        fields["firebase_credentials_json"] = credentials

    enabled = fields.get("firebase_enabled", settings.firebase_enabled)
    project_id = fields.get("firebase_project_id", settings.firebase_project_id)
    bucket = fields.get("firebase_bucket", settings.firebase_bucket)
    creds = (
        fields["firebase_credentials_json"]
        if "firebase_credentials_json" in fields
        else settings.firebase_credentials_json
    )
    _validate_firebase_payload(
        enabled=bool(enabled),
        project_id=project_id or "",
        bucket=bucket or "",
        credentials=creds or "",
    )

    translations = fields.pop("translations", None)
    for key, value in fields.items():
        setattr(settings, key, value)
    settings.save()
    if translations:
        upsert_settings_translations(settings=settings, translations=translations)
    invalidate_media_storage_cache()
    return settings


@transaction.atomic
def update_bunny_settings(*, fields: dict) -> SiteSettings:
    settings = get_site_settings()
    for secret in ("bunny_api_key", "bunny_token_key"):
        if fields.get(secret) == "":
            fields[secret] = getattr(settings, secret)

    enabled = fields.get("bunny_enabled", settings.bunny_enabled)
    library_id = fields.get("bunny_library_id", settings.bunny_library_id)
    token_key = (
        fields["bunny_token_key"] if "bunny_token_key" in fields else settings.bunny_token_key
    )
    if enabled:
        if not (library_id or "").strip() or not (token_key or "").strip():
            raise BusinessError(
                "BUNNY_CONFIG_INCOMPLETE",
                "Para activar Bunny.net necesitas library_id y token_key.",
                http_status=422,
            )

    if "bunny_cdn_hostname" in fields:
        fields["bunny_cdn_hostname"] = _normalize_bunny_hostname(fields["bunny_cdn_hostname"] or "")

    ttl = fields.get("bunny_token_ttl_seconds", settings.bunny_token_ttl_seconds)
    if ttl is not None and not (60 <= int(ttl) <= 14400):
        raise BusinessError(
            "BUNNY_TTL_INVALID",
            "El TTL del token debe estar entre 60 y 14400 segundos (1 min – 4 h).",
            http_status=422,
        )

    for key, value in fields.items():
        setattr(settings, key, value)
    settings.save()
    return settings


def _normalize_bunny_hostname(value: str) -> str:
    raw = value.strip().removeprefix("https://").removeprefix("http://")
    return raw.split("/")[0].strip()
