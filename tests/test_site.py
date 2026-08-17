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
    def test_public_site_defaults(self, api_client, languages):
        response = api_client.get("/api/v1/public/site/?lang=es")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["sliders"] == []
        assert data["start_buttons"] == []
        assert data["testimonials"] == []
        assert data["about"] == {"title": "", "html": ""}
        assert data["terms"] == {"title": "", "html": ""}
        assert data["privacy"] == {"title": "", "html": ""}
        assert data["contracting"] == {"title": "", "html": ""}

    def test_public_site_filters_by_language(self, staff_client, api_client, languages):
        staff_client.post(
            "/api/v1/admin/site/sliders/",
            {
                "is_active": True,
                "translations": [
                    {
                        "language_code": "es",
                        "title": "Hero ES",
                        "text": "Hola",
                        "link": "/cursos",
                        "link_text": "Ver",
                    },
                    {
                        "language_code": "en",
                        "title": "Hero EN",
                        "text": "Hello",
                        "link": "/courses",
                        "link_text": "See",
                    },
                ],
            },
            format="json",
        )
        staff_client.post(
            "/api/v1/admin/site/sliders/",
            {
                "is_active": False,
                "translations": [{"language_code": "es", "title": "Oculto"}],
            },
            format="json",
        )
        staff_client.post(
            "/api/v1/admin/site/start-buttons/",
            {
                "color": "#FF00AA",
                "translations": [
                    {
                        "language_code": "es",
                        "title": "Cursos",
                        "link": "/cursos",
                        "link_text": "Empezar",
                    }
                ],
            },
            format="json",
        )
        staff_client.post(
            "/api/v1/admin/site/testimonials/",
            {
                "stars": 5,
                "translations": [
                    {"language_code": "es", "name": "Ana", "comment": "Excelente"},
                    {"language_code": "en", "name": "Ana", "comment": "Excellent"},
                ],
            },
            format="json",
        )
        staff_client.patch(
            "/api/v1/admin/site/settings/",
            {
                "translations": [
                    {
                        "language_code": "es",
                        "about_title": "Sobre mí",
                        "about_html": "<p>ES</p>",
                        "terms_title": "Términos y condiciones",
                        "terms_html": "<p>Términos ES</p>",
                        "privacy_title": "Política de privacidad",
                        "privacy_html": "<p>Privacidad ES</p>",
                        "contracting_title": "Condiciones de contratación",
                        "contracting_html": "<p>Contratación ES</p>",
                    },
                    {
                        "language_code": "en",
                        "about_title": "About me",
                        "about_html": "<p>EN</p>",
                        "terms_title": "Terms and conditions",
                        "terms_html": "<p>Terms EN</p>",
                        "privacy_title": "Privacy policy",
                        "privacy_html": "<p>Privacy EN</p>",
                        "contracting_title": "Terms of sale",
                        "contracting_html": "<p>Sale EN</p>",
                    },
                ]
            },
            format="json",
        )

        es = api_client.get("/api/v1/public/site/?lang=es").json()["data"]
        assert es["sliders"][0]["title"] == "Hero ES"
        assert es["about"]["title"] == "Sobre mí"
        assert es["terms"]["title"] == "Términos y condiciones"
        assert es["privacy"]["html"] == "<p>Privacidad ES</p>"
        assert es["contracting"]["title"] == "Condiciones de contratación"
        assert es["testimonials"][0]["comment"] == "Excelente"

        en = api_client.get("/api/v1/public/site/?lang=en").json()["data"]
        assert en["sliders"][0]["title"] == "Hero EN"
        assert en["about"]["title"] == "About me"
        assert en["terms"]["title"] == "Terms and conditions"
        assert en["start_buttons"] == []

    def test_public_site_unknown_language(self, api_client, languages):
        response = api_client.get("/api/v1/public/site/?lang=fr")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "LANGUAGE_NOT_FOUND"


@pytest.mark.django_db
class TestAdminSiteSettings:
    def test_update_about_and_social(self, staff_client, languages):
        response = staff_client.patch(
            "/api/v1/admin/site/settings/",
            {
                "social_instagram": "https://instagram.com/petra",
                "phone_1": "+421 111",
                "contact_email": "hola@petralicious.sk",
                "translations": [
                    {
                        "language_code": "es",
                        "about_title": "Sobre Petra",
                        "about_html": "<p>Hola</p>",
                        "terms_title": "Términos",
                        "terms_html": "<p>Términos</p>",
                        "privacy_title": "Privacidad",
                        "privacy_html": "<p>Privacidad</p>",
                        "contracting_title": "Contratación",
                        "contracting_html": "<p>Contratación</p>",
                    }
                ],
            },
            format="json",
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["translations"][0]["about_title"] == "Sobre Petra"
        assert data["translations"][0]["terms_title"] == "Términos"
        assert data["translations"][0]["privacy_title"] == "Privacidad"
        assert data["translations"][0]["contracting_title"] == "Contratación"
        assert data["storage_backend"] == "local"
        assert "firebase_credentials_json" not in data

    def test_legal_texts_do_not_wipe_about(self, staff_client, languages):
        staff_client.patch(
            "/api/v1/admin/site/settings/",
            {
                "translations": [
                    {
                        "language_code": "es",
                        "about_title": "Sobre Petra",
                        "about_html": "<p>Hola</p>",
                    }
                ]
            },
            format="json",
        )
        response = staff_client.patch(
            "/api/v1/admin/site/settings/",
            {
                "translations": [
                    {
                        "language_code": "es",
                        "terms_title": "Términos",
                        "terms_html": "<p>Términos</p>",
                    }
                ]
            },
            format="json",
        )
        assert response.status_code == 200
        row = response.json()["data"]["translations"][0]
        assert row["about_title"] == "Sobre Petra"
        assert row["terms_title"] == "Términos"

        public = staff_client.get("/api/v1/public/site/?lang=es").json()["data"]
        assert public["about"]["title"] == "Sobre Petra"
        assert public["terms"]["title"] == "Términos"

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
    def test_slider_with_image(self, staff_client, languages):
        response = staff_client.post(
            "/api/v1/admin/site/sliders/",
            {
                "translations": '[{"language_code":"es","title":"Banner"}]',
                "background_image": _make_image(),
            },
            format="multipart",
        )
        assert response.status_code == 201
        body = response.json()["data"]
        assert body["background_image_url"] is not None
        assert body["translations"][0]["title"] == "Banner"

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
            {
                "name": "News",
                "email": "news@example.com",
                "language": "es",
                "consent": True,
            },
            format="json",
        )
        assert first.status_code == 201

        duplicate = api_client.post(
            "/api/v1/public/newsletter/",
            {
                "name": "News",
                "email": "news@example.com",
                "language": "es",
                "consent": True,
            },
            format="json",
        )
        assert duplicate.status_code == 409

        listing = staff_client.get("/api/v1/admin/newsletter/")
        assert listing.json()["count"] == 1
        assert listing.json()["results"][0]["email"] == "news@example.com"
