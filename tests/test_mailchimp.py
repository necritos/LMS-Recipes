from unittest.mock import MagicMock, patch

import pytest
from django.core import mail

from apps.site.selectors import get_site_settings

MAILCHIMP_KEY = "test-mailchimp-marketing-key-us21"
AUDIENCE = "60e8a3969d"
TRANSACTIONAL_KEY = "test-mandrill-transactional-key"


def _enable_mailchimp(staff_client, **overrides):
    payload = {
        "mailchimp_enabled": True,
        "mailchimp_api_key": MAILCHIMP_KEY,
        "mailchimp_audience_id": AUDIENCE,
        "mailchimp_audience_name": "Petralicious",
        "mailchimp_interest_es_id": "int-es",
        "mailchimp_interest_sk_id": "int-sk",
        "mailchimp_from_email": "hola@petralicious.sk",
        "mailchimp_from_name": "Petralicious",
    }
    payload.update(overrides)
    response = staff_client.patch("/api/v1/admin/site/mailchimp/", payload, format="json")
    assert response.status_code == 200, response.json()
    return response.json()["data"]


def _subscribe_payload(**overrides):
    payload = {
        "name": "Ana Pérez",
        "email": "ana@example.com",
        "language": "es",
        "consent": True,
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
class TestAdminMailchimpSettings:
    def test_get_does_not_expose_secrets(self, staff_client):
        _enable_mailchimp(staff_client, mailchimp_transactional_api_key=TRANSACTIONAL_KEY)
        data = staff_client.get("/api/v1/admin/site/mailchimp/").json()["data"]
        assert data["mailchimp_enabled"] is True
        assert data["mailchimp_configured"] is True
        assert data["mailchimp_transactional_configured"] is True
        assert data["mailchimp_server_prefix"] == "us21"
        assert data["mailchimp_audience_id"] == AUDIENCE
        assert "mailchimp_api_key" not in data
        assert "mailchimp_transactional_api_key" not in data
        assert MAILCHIMP_KEY not in str(data)
        assert TRANSACTIONAL_KEY not in str(data)

    def test_enable_requires_key_and_audience(self, staff_client):
        response = staff_client.patch(
            "/api/v1/admin/site/mailchimp/",
            {"mailchimp_enabled": True, "mailchimp_audience_id": AUDIENCE},
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "MAILCHIMP_CONFIG_INCOMPLETE"

    def test_invalid_api_key(self, staff_client):
        response = staff_client.patch(
            "/api/v1/admin/site/mailchimp/",
            {
                "mailchimp_enabled": True,
                "mailchimp_api_key": "not-a-mailchimp-key",
                "mailchimp_audience_id": AUDIENCE,
            },
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "MAILCHIMP_API_KEY_INVALID"

    def test_blank_key_preserves_existing(self, staff_client):
        _enable_mailchimp(staff_client)
        patched = staff_client.patch(
            "/api/v1/admin/site/mailchimp/",
            {"mailchimp_api_key": "", "mailchimp_audience_name": "Petralicious"},
            format="json",
        )
        assert patched.status_code == 200
        settings = get_site_settings()
        assert settings.mailchimp_api_key == MAILCHIMP_KEY


@pytest.mark.django_db
class TestNewsletterPublic:
    def test_subscribe_without_mailchimp_is_skipped(self, api_client, staff_client):
        first = api_client.post(
            "/api/v1/public/newsletter/",
            _subscribe_payload(),
            format="json",
        )
        assert first.status_code == 201

        duplicate = api_client.post(
            "/api/v1/public/newsletter/",
            _subscribe_payload(),
            format="json",
        )
        assert duplicate.status_code == 409

        listing = staff_client.get("/api/v1/admin/newsletter/")
        assert listing.json()["count"] == 1
        row = listing.json()["results"][0]
        assert row["email"] == "ana@example.com"
        assert row["name"] == "Ana Pérez"
        assert row["language"] == "es"
        assert row["consent"] is True
        assert row["mailchimp_synced"] is False
        assert row["mailchimp_status"] == "skipped"
        assert row["mailchimp_destination"] == ""

    def test_consent_required(self, api_client):
        response = api_client.post(
            "/api/v1/public/newsletter/",
            _subscribe_payload(consent=False),
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "CONSENT_REQUIRED"

    def test_language_must_be_es_or_sk(self, api_client):
        response = api_client.post(
            "/api/v1/public/newsletter/",
            _subscribe_payload(language="en"),
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "NEWSLETTER_LANGUAGE_INVALID"

    def test_invalid_tag(self, api_client):
        response = api_client.post(
            "/api/v1/public/newsletter/",
            _subscribe_payload(tags=["not valid"]),
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "NEWSLETTER_TAG_INVALID"


@pytest.mark.django_db(transaction=True)
class TestNewsletterMailchimpSync:
    def test_es_syncs_group_and_web_tag(self, staff_client, api_client):
        _enable_mailchimp(staff_client)
        calls: list[tuple] = []

        def fake_request(site, method, path, json=None, params=None):
            calls.append((method, path, json))
            return {}

        with patch(
            "apps.site.services.mailchimp_service._marketing_request",
            side_effect=fake_request,
        ):
            response = api_client.post(
                "/api/v1/public/newsletter/",
                _subscribe_payload(tags=["FREEBIE_ES"]),
                format="json",
            )
        assert response.status_code == 201, response.json()

        row = staff_client.get("/api/v1/admin/newsletter/").json()["results"][0]
        assert row["mailchimp_synced"] is True
        assert row["mailchimp_status"] == "synced"
        assert row["mailchimp_audience_id"] == AUDIENCE
        assert row["mailchimp_audience_name"] == "Petralicious"
        assert row["mailchimp_group"] == "Español"
        assert row["mailchimp_tags"] == ["WEB_ES", "FREEBIE_ES"]
        assert "Petralicious" in row["mailchimp_destination"]
        assert "Español" in row["mailchimp_destination"]
        assert "WEB_ES" in row["mailchimp_destination"]

        methods = [item[0] for item in calls]
        assert "PUT" in methods
        assert "POST" in methods
        put_body = next(item[2] for item in calls if item[0] == "PUT")
        assert put_body["interests"]["int-es"] is True
        assert put_body["interests"]["int-sk"] is False
        assert put_body["merge_fields"]["FNAME"] == "Ana"
        tag_body = next(item[2] for item in calls if item[0] == "POST")
        names = {item["name"] for item in tag_body["tags"]}
        assert names == {"WEB_ES", "FREEBIE_ES"}

    def test_sk_uses_slovak_group(self, staff_client, api_client):
        _enable_mailchimp(staff_client)

        def fake_request(site, method, path, json=None, params=None):
            return {}

        with patch(
            "apps.site.services.mailchimp_service._marketing_request",
            side_effect=fake_request,
        ):
            api_client.post(
                "/api/v1/public/newsletter/",
                _subscribe_payload(language="sk", email="jana@example.com"),
                format="json",
            )

        row = staff_client.get("/api/v1/admin/newsletter/").json()["results"][0]
        assert row["language"] == "sk"
        assert row["mailchimp_group"] == "Slovenčina"
        assert row["mailchimp_tags"] == ["WEB_SK"]

    def test_failed_sync_is_visible(self, staff_client, api_client):
        _enable_mailchimp(staff_client)
        from apps.common.exceptions import BusinessError

        def boom(site, method, path, json=None, params=None):
            raise BusinessError("MAILCHIMP_API_ERROR", "Audience gone", http_status=422)

        with patch(
            "apps.site.services.mailchimp_service._marketing_request",
            side_effect=boom,
        ):
            response = api_client.post(
                "/api/v1/public/newsletter/",
                _subscribe_payload(),
                format="json",
            )
        assert response.status_code == 201
        row = staff_client.get("/api/v1/admin/newsletter/").json()["results"][0]
        assert row["mailchimp_synced"] is False
        assert row["mailchimp_status"] == "failed"
        assert "Audience gone" in row["mailchimp_error"]

    def test_interests_endpoint(self, staff_client):
        _enable_mailchimp(staff_client)

        def fake_request(site, method, path, json=None, params=None):
            if path.endswith("interest-categories"):
                return {"categories": [{"id": "cat1", "title": "Idioma / Jazyk", "type": "hidden"}]}
            return {
                "interests": [
                    {"id": "int-es", "name": "Español"},
                    {"id": "int-sk", "name": "Slovenčina"},
                ]
            }

        with patch(
            "apps.site.services.mailchimp_service._marketing_request",
            side_effect=fake_request,
        ):
            response = staff_client.get("/api/v1/admin/site/mailchimp/interests/")
        assert response.status_code == 200
        categories = response.json()["data"]["categories"]
        assert categories[0]["title"] == "Idioma / Jazyk"
        names = {item["name"] for item in categories[0]["interests"]}
        assert names == {"Español", "Slovenčina"}

    def test_resync_and_filter(self, staff_client, api_client):
        _enable_mailchimp(staff_client)
        from apps.common.exceptions import BusinessError

        def boom(site, method, path, json=None, params=None):
            raise BusinessError("MAILCHIMP_API_ERROR", "fail", http_status=422)

        with patch(
            "apps.site.services.mailchimp_service._marketing_request",
            side_effect=boom,
        ):
            api_client.post("/api/v1/public/newsletter/", _subscribe_payload(), format="json")

        subscriber_id = staff_client.get("/api/v1/admin/newsletter/").json()["results"][0]["id"]
        failed = staff_client.get("/api/v1/admin/newsletter/?mailchimp_status=failed")
        assert failed.json()["count"] == 1

        with patch(
            "apps.site.services.mailchimp_service._marketing_request",
            return_value={},
        ):
            resync = staff_client.post(f"/api/v1/admin/newsletter/{subscriber_id}/resync/")
        assert resync.status_code == 200
        assert resync.json()["data"]["mailchimp_status"] == "synced"


@pytest.mark.django_db
class TestMailchimpTransactional:
    def test_password_reset_uses_mandrill_when_configured(
        self, staff_client, api_client, registered_user
    ):
        _enable_mailchimp(staff_client, mailchimp_transactional_api_key=TRANSACTIONAL_KEY)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"[]"
        mock_response.json.return_value = [{"status": "sent", "email": "user@recetario.local"}]

        with patch(
            "apps.site.services.mailchimp_service.requests.post",
            return_value=mock_response,
        ) as post:
            mail.outbox.clear()
            forgot = api_client.post(
                "/api/v1/auth/password/forgot/",
                {"email": "user@recetario.local"},
                format="json",
            )
        assert forgot.status_code == 200
        assert post.called
        assert post.call_args.kwargs["json"]["key"] == TRANSACTIONAL_KEY
        assert mail.outbox == []
