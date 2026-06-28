import re

import pytest
from django.core import mail


@pytest.mark.django_db
class TestUserRegistration:
    def test_register_returns_tokens(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "new@recetario.local",
                "password": "securepass123",
                "password_confirm": "securepass123",
                "first_name": "Ana",
                "last_name": "López",
                "terms_accepted": True,
            },
            format="json",
        )
        assert response.status_code == 201
        body = response.json()
        assert body["data"]["email"] == "new@recetario.local"
        assert "access" in body["data"]
        assert "refresh" in body["data"]

    @pytest.mark.django_db(transaction=True)
    def test_register_sends_welcome_email(self, api_client):
        api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "welcome@recetario.local",
                "password": "securepass123",
                "password_confirm": "securepass123",
                "terms_accepted": True,
            },
            format="json",
        )
        assert len(mail.outbox) == 1
        assert "Bienvenido" in mail.outbox[0].subject

    def test_register_duplicate_email(self, api_client, registered_user):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "user@recetario.local",
                "password": "securepass123",
                "password_confirm": "securepass123",
                "terms_accepted": True,
            },
            format="json",
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


@pytest.mark.django_db
class TestUserLogin:
    def test_login_success(self, api_client, registered_user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": "user@recetario.local", "password": "userpass123"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["data"]["user"]["email"] == "user@recetario.local"

    def test_login_invalid_credentials(self, api_client, registered_user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": "user@recetario.local", "password": "wrongpassword"},
            format="json",
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"

    def test_logout(self, auth_client, registered_user):
        response = auth_client.post(
            "/api/v1/auth/logout/",
            {"refresh": registered_user["refresh"]},
            format="json",
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestStaffAuth:
    def test_admin_login(self, api_client, staff_user):
        response = api_client.post(
            "/api/v1/admin/auth/login/",
            {"email": "admin@recetario.local", "password": "adminpass123"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["data"]["user"]["email"] == "admin@recetario.local"

    def test_user_cannot_access_admin_logout(self, auth_client, registered_user):
        response = auth_client.post(
            "/api/v1/admin/auth/logout/",
            {"refresh": registered_user["refresh"]},
            format="json",
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestPasswordReset:
    @pytest.mark.django_db(transaction=True)
    def test_password_reset_flow(self, api_client, registered_user):
        forgot = api_client.post(
            "/api/v1/auth/password/forgot/",
            {"email": "user@recetario.local"},
            format="json",
        )
        assert forgot.status_code == 200
        assert len(mail.outbox) >= 1

        reset_mail = mail.outbox[-1]
        match = re.search(r"\b(\d{6})\b", reset_mail.body)
        assert match is not None
        code = match.group(1)

        verify = api_client.post(
            "/api/v1/auth/password/verify-code/",
            {"email": "user@recetario.local", "code": code},
            format="json",
        )
        assert verify.status_code == 200

        reset = api_client.post(
            "/api/v1/auth/password/reset/",
            {
                "email": "user@recetario.local",
                "code": code,
                "password": "newpass12345",
                "password_confirm": "newpass12345",
            },
            format="json",
        )
        assert reset.status_code == 200

        login = api_client.post(
            "/api/v1/auth/login/",
            {"email": "user@recetario.local", "password": "newpass12345"},
            format="json",
        )
        assert login.status_code == 200


@pytest.mark.django_db
class TestGoogleAuth:
    def test_google_auth_creates_user(self, api_client, settings, monkeypatch):
        settings.GOOGLE_CLIENT_ID = "test-client-id.apps.googleusercontent.com"

        def fake_verify(token, request, audience):
            assert token == "valid-google-token"
            assert audience == settings.GOOGLE_CLIENT_ID
            return {
                "sub": "google-user-123",
                "email": "google@recetario.local",
                "email_verified": True,
                "given_name": "Google",
                "family_name": "User",
            }

        monkeypatch.setattr(
            "apps.accounts.services.google_auth.id_token.verify_oauth2_token",
            fake_verify,
        )

        response = api_client.post(
            "/api/v1/auth/google/",
            {"id_token": "valid-google-token"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["data"]["created"] is True
        assert response.json()["data"]["user"]["email"] == "google@recetario.local"

    def test_google_not_configured(self, api_client, settings):
        settings.GOOGLE_CLIENT_ID = ""
        response = api_client.post(
            "/api/v1/auth/google/",
            {"id_token": "any"},
            format="json",
        )
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "GOOGLE_NOT_CONFIGURED"
