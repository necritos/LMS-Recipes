import os
from pathlib import Path

from django.conf import settings


def _use_s3_storage() -> bool:
    return bool(os.environ.get("AWS_STORAGE_BUCKET_NAME"))


def get_media_storage_backend() -> str:
    if _use_s3_storage():
        return "apps.common.storage.RecetarioMediaStorage"
    return "django.core.files.storage.FileSystemStorage"


def configure_media_storage() -> None:
    backend = get_media_storage_backend()
    if not hasattr(settings, "STORAGES"):
        settings.STORAGES = {  # type: ignore[attr-defined]
            "default": {"BACKEND": backend},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            },
        }
    else:
        settings.STORAGES["default"]["BACKEND"] = backend  # type: ignore[attr-defined]

    if _use_s3_storage():
        settings.AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
        settings.AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
        settings.AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
        settings.AWS_S3_ENDPOINT_URL = os.environ.get(
            "AWS_S3_ENDPOINT_URL",
            "https://nyc3.digitaloceanspaces.com",
        )
        settings.AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "nyc3")
        settings.AWS_DEFAULT_ACL = "public-read"
        settings.AWS_QUERYSTRING_AUTH = False
        settings.AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
        custom_domain = os.environ.get("AWS_S3_CUSTOM_DOMAIN")
        if custom_domain:
            settings.AWS_S3_CUSTOM_DOMAIN = custom_domain
        settings.MEDIA_URL = os.environ.get(
            "MEDIA_URL",
            f"https://{settings.AWS_STORAGE_BUCKET_NAME}.{settings.AWS_S3_REGION_NAME}.digitaloceanspaces.com/",
        )
    else:
        settings.MEDIA_URL = "/media/"
        settings.MEDIA_ROOT = Path(settings.BASE_DIR) / "media"  # type: ignore[attr-defined]
