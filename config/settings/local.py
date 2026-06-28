import os

from config.settings.base import *  # noqa: F403
from config.settings.base import _env_csv
from config.settings.database import get_default_database

DEBUG = True

CORS_ALLOWED_ORIGINS = _env_csv("CORS_ALLOWED_ORIGINS", "http://localhost:5173")

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

if os.environ.get("DATABASE_URL"):
    DATABASES = {"default": get_default_database()}  # noqa: F405
else:
    DATABASES = {  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }
