from __future__ import annotations

import hashlib
import io
import json
import logging
import os
from urllib.parse import quote

from django.core.files.storage import FileSystemStorage, Storage
from django.utils.deconstruct import deconstructible

logger = logging.getLogger(__name__)

_cache: tuple[str, Storage] | None = None


def invalidate_media_storage_cache() -> None:
    global _cache
    _cache = None


def active_storage_kind() -> str:
    return _storage_cache_key().split(":")[0]


def resolve_media_storage() -> Storage:
    global _cache
    key = _storage_cache_key()
    if _cache is not None and _cache[0] == key:
        return _cache[1]
    inner = _build_storage()
    _cache = (key, inner)
    return inner


def _storage_cache_key() -> str:
    row = _load_firebase_settings()
    if row and row.get("enabled"):
        digest = hashlib.sha256((row.get("credentials_json") or "").encode("utf-8")).hexdigest()[
            :16
        ]
        return f"firebase:{row.get('bucket')}:{digest}"
    if os.environ.get("AWS_STORAGE_BUCKET_NAME"):
        return f"s3:{os.environ['AWS_STORAGE_BUCKET_NAME']}"
    return "local"


def _load_firebase_settings() -> dict | None:
    try:
        from django.apps import apps
        from django.db.utils import OperationalError, ProgrammingError

        if not apps.ready or not apps.is_installed("apps.site"):
            return None

        from apps.site.models import SiteSettings

        row = SiteSettings.objects.filter(singleton_key="default").first()
        if row is None:
            return None
        return {
            "enabled": row.firebase_enabled,
            "project_id": row.firebase_project_id,
            "bucket": row.firebase_bucket,
            "credentials_json": row.firebase_credentials_json,
        }
    except (OperationalError, ProgrammingError, ImportError):
        return None
    except Exception:
        logger.exception("No se pudo leer la configuración de Firebase Storage.")
        return None


def _build_storage() -> Storage:
    row = _load_firebase_settings()
    if (
        row
        and row.get("enabled")
        and row.get("bucket")
        and row.get("credentials_json")
        and row.get("project_id")
    ):
        try:
            return build_firebase_storage(
                project_id=row["project_id"],
                bucket=row["bucket"],
                credentials_json=row["credentials_json"],
            )
        except Exception:
            logger.exception("Falló la inicialización de Firebase Storage; se usa fallback.")

    if os.environ.get("AWS_STORAGE_BUCKET_NAME"):
        return RecetarioMediaStorage()

    return FileSystemStorage()


def build_firebase_storage(*, project_id: str, bucket: str, credentials_json: str) -> Storage:
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import storage as fb_storage

    cred_dict = json.loads(credentials_json)
    digest = hashlib.sha256(credentials_json.encode("utf-8")).hexdigest()[:12]
    app_name = f"recetario-storage-{digest}"
    try:
        app = firebase_admin.get_app(app_name)
    except ValueError:
        cred = credentials.Certificate(cred_dict)
        app = firebase_admin.initialize_app(
            cred,
            {"storageBucket": bucket, "projectId": project_id},
            name=app_name,
        )
    return FirebaseStorage(bucket=fb_storage.bucket(app=app))


class RecetarioMediaStorage(Storage):
    """DO Spaces (S3-compatible). Fallback si Firebase no está activo."""

    location = "media"
    default_acl = "public-read"
    file_overwrite = False

    def __init__(self, **kwargs):
        from storages.backends.s3boto3 import S3Boto3Storage

        self._s3 = S3Boto3Storage(
            location=self.location,
            default_acl=self.default_acl,
            file_overwrite=self.file_overwrite,
            **kwargs,
        )

    def _save(self, name, content):
        return self._s3._save(name, content)

    def url(self, name):
        return self._s3.url(name)

    def exists(self, name):
        return self._s3.exists(name)

    def delete(self, name):
        return self._s3.delete(name)

    def size(self, name):
        return self._s3.size(name)

    def _open(self, name, mode="rb"):
        return self._s3._open(name, mode)


@deconstructible
class FirebaseStorage(Storage):
    def __init__(self, bucket):
        self.bucket = bucket

    def _save(self, name, content):
        name = self.get_valid_name(name)
        blob = self.bucket.blob(name)
        if hasattr(content, "seek"):
            content.seek(0)
        content_type = getattr(content, "content_type", None) or "application/octet-stream"
        blob.upload_from_file(content, content_type=content_type)
        try:
            blob.make_public()
        except Exception:
            logger.info("No se pudo hacer público el blob (ACL uniforme); se usa URL alt=media.")
        return name

    def url(self, name):
        encoded = quote(name, safe="")
        return (
            f"https://firebasestorage.googleapis.com/v0/b/{self.bucket.name}/o/{encoded}?alt=media"
        )

    def exists(self, name):
        return self.bucket.blob(name).exists()

    def delete(self, name):
        blob = self.bucket.blob(name)
        if blob.exists():
            blob.delete()

    def size(self, name):
        blob = self.bucket.blob(name)
        blob.reload()
        return blob.size or 0

    def _open(self, name, mode="rb"):
        data = self.bucket.blob(name).download_as_bytes()
        return io.BytesIO(data)


@deconstructible
class RecetarioDynamicStorage(Storage):
    """Firebase (si el admin lo configuró) → Spaces → filesystem local."""

    def _inner(self) -> Storage:
        return resolve_media_storage()

    def _save(self, name, content):
        return self._inner()._save(name, content)

    def url(self, name):
        return self._inner().url(name)

    def exists(self, name):
        return self._inner().exists(name)

    def delete(self, name):
        return self._inner().delete(name)

    def size(self, name):
        return self._inner().size(name)

    def _open(self, name, mode="rb"):
        return self._inner()._open(name, mode)

    def get_valid_name(self, name):
        return self._inner().get_valid_name(name)

    def get_available_name(self, name, max_length=None):
        return self._inner().get_available_name(name, max_length=max_length)
