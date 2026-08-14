import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def _make_image(name: str = "cover.png") -> SimpleUploadedFile:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), color="blue").save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/png")


@pytest.mark.django_db
class TestPublicSite:
    def test_public_site_defaults(self, api_client):
        response = api_client.get("/api/v1/public/site/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["sliders"] == []
        assert data["start_buttons"] == []
        assert data["testimonials"] == []
        assert "about" in data
        assert "social" in data
        assert "contact_info" in data

    def test_public_site_includes_active_content(self, staff_client, api_client):
        staff_client.post(
            "/api/v1/admin/site/sliders/",
            {
                "title": "Hero",
                "text": "Hola",
                "link": "/cursos",
                "link_text": "Ver",
                "is_active": True,
            },
            format="json",
        )
        staff_client.post(
            "/api/v1/admin/site/sliders/",
            {"title": "Oculto", "is_active": False},
            format="json",
        )
        staff_client.post(
            "/api/v1/admin/site/start-buttons/",
            {
                "title": "Cursos",
                "color": "#FF00AA",
                "link": "/cursos",
                "link_text": "Empezar",
            },
            format="json",
        )
        staff_client.post(
            "/api/v1/admin/site/testimonials/",
            {"stars": 5, "comment": "Excelente", "name": "Ana"},
            format="json",
        )
        response = api_client.get("/api/v1/public/site/")
        data = response.json()["data"]
        assert len(data["sliders"]) == 1
        assert data["sliders"][0]["title"] == "Hero"
        assert data["start_buttons"][0]["color"] == "#FF00AA"
        assert data["testimonials"][0]["stars"] == 5


@pytest.mark.django_db
class TestAdminSiteSettings:
    def test_update_about_and_social(self, staff_client):
        response = staff_client.patch(
            "/api/v1/admin/site/settings/",
            {
                "about_title": "Sobre Petra",
                "about_html": "<p>Hola</p>",
                "social_instagram": "https://instagram.com/petra",
                "phone_1": "+421 111",
                "contact_email": "hola@petralicious.sk",
            },
            format="json",
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["about_title"] == "Sobre Petra"
        assert data["storage_backend"] == "local"
        assert "firebase_credentials_json" not in data

    def test_firebase_requires_complete_config(self, staff_client):
        response = staff_client.patch(
            "/api/v1/admin/site/settings/",
            {"firebase_enabled": True, "firebase_project_id": "demo"},
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "FIREBASE_CONFIG_INCOMPLETE"

    def test_firebase_invalid_json(self, staff_client):
        response = staff_client.patch(
            "/api/v1/admin/site/settings/",
            {
                "firebase_enabled": True,
                "firebase_project_id": "demo",
                "firebase_bucket": "demo.appspot.com",
                "firebase_credentials_json": "{not-json",
            },
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "FIREBASE_CREDENTIALS_INVALID"

    def test_firebase_valid_service_account_saved(self, staff_client):
        response = staff_client.patch(
            "/api/v1/admin/site/settings/",
            {
                "firebase_enabled": True,
                "firebase_project_id": "demo",
                "firebase_bucket": "demo.appspot.com",
                "firebase_credentials_json": (
                    '{"type":"service_account","project_id":"demo",'
                    '"private_key":"x","client_email":"a@b.c"}'
                ),
            },
            format="json",
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["firebase_enabled"] is True
        assert data["firebase_configured"] is True
        assert "private_key" not in str(data)


@pytest.mark.django_db
class TestAdminSiteContent:
    def test_slider_with_image(self, staff_client):
        response = staff_client.post(
            "/api/v1/admin/site/sliders/",
            {"title": "Banner", "background_image": _make_image()},
            format="multipart",
        )
        assert response.status_code == 201
        assert response.json()["data"]["background_image_url"] is not None

    def test_admin_requires_staff(self, api_client):
        response = api_client.get("/api/v1/admin/site/settings/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestContactAndNewsletter:
    def test_contact_flow(self, api_client, staff_client):
        created = api_client.post(
            "/api/v1/public/contact/",
            {
                "name": "María",
                "email": "maria@example.com",
                "topic": "Cursos",
                "message": "Quiero info",
            },
            format="json",
        )
        assert created.status_code == 201

        listing = staff_client.get("/api/v1/admin/contact/")
        assert listing.status_code == 200
        item = listing.json()["results"][0]
        assert item["is_read"] is False
        message_id = item["id"]

        patched = staff_client.patch(
            f"/api/v1/admin/contact/{message_id}/",
            {"is_read": True},
            format="json",
        )
        assert patched.status_code == 200
        assert patched.json()["data"]["is_read"] is True

        unread = staff_client.get("/api/v1/admin/contact/?is_read=false")
        assert unread.json()["count"] == 0

    def test_newsletter_subscribe_and_duplicate(self, api_client, staff_client):
        first = api_client.post(
            "/api/v1/public/newsletter/",
            {"email": "news@example.com"},
            format="json",
        )
        assert first.status_code == 201

        duplicate = api_client.post(
            "/api/v1/public/newsletter/",
            {"email": "news@example.com"},
            format="json",
        )
        assert duplicate.status_code == 409

        listing = staff_client.get("/api/v1/admin/newsletter/")
        assert listing.json()["count"] == 1
        assert listing.json()["results"][0]["email"] == "news@example.com"
