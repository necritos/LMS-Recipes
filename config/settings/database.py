import os
import re
from urllib.parse import parse_qs, unquote, urlparse

# postgres://user:password@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE
_CLOUDSQL_URL = re.compile(
    r"^postgres(?:ql)?://(.+)@/([^?]+)(?:\?(.*))?$",
    re.IGNORECASE,
)


def database_from_url(url: str) -> dict:
    match = _CLOUDSQL_URL.match(url.strip())
    if match:
        userinfo = match.group(1)
        user, _, password = userinfo.partition(":")
        user = unquote(user)
        password = unquote(password)
        name = match.group(2).strip("/") or "recetario"
        query = parse_qs(match.group(3) or "")
        socket_hosts = query.get("host", [])
        host = socket_hosts[0] if socket_hosts else ""
        if host.startswith("/cloudsql/"):
            return {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": name,
                "USER": user,
                "PASSWORD": password,
                "HOST": host,
                "PORT": "",
            }

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    socket_hosts = query.get("host", [])
    host = socket_hosts[0] if socket_hosts else (parsed.hostname or "")

    port: int | str = 5432
    if host.startswith("/cloudsql/"):
        port = ""
    elif parsed.netloc and ":" in parsed.netloc.rsplit("@", 1)[-1]:
        hostpart = parsed.netloc.rsplit("@", 1)[-1]
        if hostpart.startswith("["):
            port = 5432
        else:
            _, _, maybe_port = hostpart.rpartition(":")
            if maybe_port.isdigit():
                port = int(maybe_port)

    options: dict = {}
    if query.get("sslmode"):
        options["sslmode"] = query["sslmode"][0]

    db_config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": (parsed.path or "/").lstrip("/") or "recetario",
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": host,
        "PORT": str(port) if port != "" else "",
    }
    if options:
        db_config["OPTIONS"] = options
    return db_config


def get_default_database() -> dict:
    url = os.environ.get("DATABASE_URL")
    if url:
        return database_from_url(url)
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "recetario"),
        "USER": os.environ.get("POSTGRES_USER", "recetario"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "recetario"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
