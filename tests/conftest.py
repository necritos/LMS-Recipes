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
