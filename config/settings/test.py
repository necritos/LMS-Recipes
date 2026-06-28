import os

from config.settings.base import *  # noqa: F403
from config.settings.database import get_default_database

DEBUG = False

ALLOWED_HOSTS = ["*"]  # noqa: F405

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

if os.environ.get("CI") == "true" or os.environ.get("DATABASE_URL"):
    DATABASES = {"default": get_default_database()}  # noqa: F405
    if not os.environ.get("DATABASE_URL"):
        _db = DATABASES["default"].copy()
        _db["NAME"] = os.environ.get("POSTGRES_TEST_DB", "recetario_test")
        DATABASES = {"default": _db}
else:
    DATABASES = {  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
