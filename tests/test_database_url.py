from config.settings.database import database_from_url


def test_standard_postgres_url():
    url = "postgres://recetario:secret@127.0.0.1:5432/recetario"
    db = database_from_url(url)
    assert db["HOST"] == "127.0.0.1"
    assert db["PORT"] == "5432"
    assert db["PASSWORD"] == "secret"
    assert db["NAME"] == "recetario"


def test_postgres_url_with_sslmode():
    url = "postgres://recetario:secret@db.example.com:25060/recetario?sslmode=require"
    db = database_from_url(url)
    assert db["HOST"] == "db.example.com"
    assert db["OPTIONS"]["sslmode"] == "require"
