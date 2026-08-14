import hashlib
from datetime import UTC, datetime
from time import time

from apps.common.exceptions import BusinessError
from apps.content.models import VideoAccessToken
from apps.site.selectors import get_site_settings


def _normalize_cdn_hostname(value: str) -> str:
    raw = (value or "").strip()
    raw = raw.removeprefix("https://").removeprefix("http://")
    return raw.split("/")[0].strip()


def sign_bunny_video(*, video_id: str) -> dict:
    video_id = (video_id or "").strip()
    if not video_id:
        raise BusinessError(
            "VIDEO_NOT_FOUND",
            "Este contenido no tiene video asignado.",
            http_status=404,
        )
    settings = get_site_settings()
    library_id = (settings.bunny_library_id or "").strip()
    token_key = (settings.bunny_token_key or "").strip()
    if not settings.bunny_enabled or not library_id or not token_key:
        raise BusinessError(
            "BUNNY_NOT_CONFIGURED",
            "Bunny.net no está configurado. Actívalo en el admin.",
            http_status=503,
        )
    ttl = int(settings.bunny_token_ttl_seconds or 3600)
    expires = int(time()) + ttl
    token = hashlib.sha256(f"{token_key}{video_id}{expires}".encode()).hexdigest()
    embed_url = (
        f"https://iframe.mediadelivery.net/embed/{library_id}/{video_id}"
        f"?token={token}&expires={expires}"
    )
    hostname = _normalize_cdn_hostname(settings.bunny_cdn_hostname)
    hls_url = None
    if hostname:
        hls_url = f"https://{hostname}/{video_id}/playlist.m3u8?token={token}&expires={expires}"
    expires_at = datetime.fromtimestamp(expires, tz=UTC)
    return {
        "signed_video_url": embed_url,
        "hls_url": hls_url,
        "expires_at": expires_at,
        "token": token,
        "video_id": video_id,
        "expires": expires,
    }


def issue_signed_video(*, user, video_id: str, lesson=None, recipe=None) -> dict:
    payload = sign_bunny_video(video_id=video_id)
    VideoAccessToken.objects.create(
        user=user,
        lesson=lesson,
        recipe=recipe,
        bunny_video_id=payload["video_id"],
        token=payload["token"],
        expires_at=payload["expires_at"],
    )
    return {
        "signed_video_url": payload["signed_video_url"],
        "hls_url": payload["hls_url"],
        "expires_at": payload["expires_at"],
    }
