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

    def test_google_auth_uses_admin_client_id(
        self, api_client, staff_client, settings, monkeypatch
    ):
        settings.GOOGLE_CLIENT_ID = "env-should-be-ignored.apps.googleusercontent.com"
        admin_client_id = "admin-client-id.apps.googleusercontent.com"
        patched = staff_client.patch(
            "/api/v1/admin/site/google/",
            {
                "google_oauth_enabled": True,
                "google_client_id": admin_client_id,
                "google_client_secret": "GOCSPX-test-secret",
            },
            format="json",
        )
        assert patched.status_code == 200, patched.json()
        assert patched.json()["data"]["google_configured"] is True
        assert "google_client_secret" not in patched.json()["data"]

        def fake_verify(token, request, audience):
            assert audience == admin_client_id
            return {
                "sub": "google-admin-1",
                "email": "admin-google@recetario.local",
                "email_verified": True,
                "given_name": "Ada",
                "family_name": "Lovelace",
            }

        monkeypatch.setattr(
            "apps.accounts.services.google_auth.id_token.verify_oauth2_token",
            fake_verify,
        )
        response = api_client.post(
            "/api/v1/auth/google/",
            {"id_token": "token"},
            format="json",
        )
        assert response.status_code == 201

        public = api_client.get("/api/v1/public/google-oauth/")
        assert public.status_code == 200
        assert public.json()["data"]["enabled"] is True
        assert public.json()["data"]["client_id"] == admin_client_id

    def test_google_admin_requires_client_id(self, staff_client):
        response = staff_client.patch(
            "/api/v1/admin/site/google/",
            {"google_oauth_enabled": True},
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "GOOGLE_CONFIG_INCOMPLETE"

    def test_google_admin_rejects_bad_client_id(self, staff_client):
        response = staff_client.patch(
            "/api/v1/admin/site/google/",
            {
                "google_oauth_enabled": True,
                "google_client_id": "not-a-google-client",
            },
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "GOOGLE_CLIENT_ID_INVALID"
