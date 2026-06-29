import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

StaffUser = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def staff_user(db):
    return StaffUser.objects.create_user(
        email="admin@recetario.local",
        password="adminpass123",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def registered_user(db, api_client):
    response = api_client.post(
        "/api/v1/auth/register/",
        {
            "email": "user@recetario.local",
            "password": "userpass123",
            "password_confirm": "userpass123",
            "terms_accepted": True,
        },
        format="json",
    )
    assert response.status_code == 201
    return response.json()["data"]


@pytest.fixture
def auth_client(api_client, registered_user):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {registered_user['access']}")
    return api_client


@pytest.fixture
def languages(db):
    from apps.catalog.models import Language

    es, _ = Language.objects.get_or_create(code="es", defaults={"name": "Español"})
    en, _ = Language.objects.get_or_create(code="en", defaults={"name": "English"})
    return {"es": es, "en": en}


@pytest.fixture
def published_course(staff_client, languages):
    response = staff_client.post(
        "/api/v1/admin/courses/",
        {
            "slug": "curso-pasta",
            "price": "49.99",
            "access_days": 365,
            "status": "published",
            "translations": [
                {
                    "language_code": "es",
                    "title": "Curso de Pasta",
                    "description": "Aprende pasta italiana",
                    "meta_title": "Pasta ES",
                    "meta_description": "Meta pasta",
                },
                {
                    "language_code": "en",
                    "title": "Pasta Course",
                    "description": "Learn Italian pasta",
                    "meta_title": "Pasta EN",
                    "meta_description": "Pasta meta",
                },
            ],
        },
        format="json",
    )
    assert response.status_code == 201
    return response.json()["data"]


@pytest.fixture
def staff_client(api_client, staff_user):
    response = api_client.post(
        "/api/v1/admin/auth/login/",
        {"email": "admin@recetario.local", "password": "adminpass123"},
        format="json",
    )
    assert response.status_code == 200
    token = response.json()["data"]["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client
