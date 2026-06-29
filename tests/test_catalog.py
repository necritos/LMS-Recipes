import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def _make_image(name: str = "cover.png") -> SimpleUploadedFile:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), color="red").save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/png")


@pytest.mark.django_db
class TestPublicCatalog:
    def test_list_languages(self, api_client, languages):
        response = api_client.get("/api/v1/public/languages/")
        assert response.status_code == 200
        body = response.json()
        assert body["data"][0]["code"] in {"en", "es"}

    def test_public_courses_filter_by_language(self, api_client, published_course):
        es = api_client.get("/api/v1/public/courses/?lang=es")
        assert es.status_code == 200
        assert es.json()["results"][0]["title"] == "Curso de Pasta"

        en = api_client.get("/api/v1/public/courses/?lang=en")
        assert en.status_code == 200
        assert en.json()["results"][0]["title"] == "Pasta Course"

    def test_public_course_detail(self, api_client, published_course):
        response = api_client.get("/api/v1/public/courses/curso-pasta/?lang=es")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["slug"] == "curso-pasta"
        assert data["meta_title"] == "Pasta ES"

    def test_draft_course_not_public(self, api_client, staff_client, languages):
        staff_client.post(
            "/api/v1/admin/courses/",
            {
                "slug": "borrador",
                "price": "10.00",
                "status": "draft",
                "translations": [
                    {"language_code": "es", "title": "Borrador", "description": "x"},
                ],
            },
            format="json",
        )
        response = api_client.get("/api/v1/public/courses/?lang=es")
        slugs = [item["slug"] for item in response.json()["results"]]
        assert "borrador" not in slugs


@pytest.mark.django_db
class TestAdminCatalog:
    def test_create_course_bilingual(self, staff_client, languages):
        response = staff_client.post(
            "/api/v1/admin/courses/",
            {
                "slug": "curso-sushi",
                "price": "59.99",
                "status": "published",
                "translations": [
                    {"language_code": "es", "title": "Sushi", "description": "ES"},
                    {"language_code": "en", "title": "Sushi EN", "description": "EN"},
                ],
            },
            format="json",
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert len(data["translations"]) == 2

    def test_upload_cover_image(self, staff_client, languages):
        create = staff_client.post(
            "/api/v1/admin/courses/",
            {
                "slug": "curso-imagen",
                "price": "19.99",
                "status": "published",
                "translations": [
                    {"language_code": "es", "title": "Con imagen", "description": "desc"},
                ],
            },
            format="json",
        )
        assert create.status_code == 201

        patch = staff_client.patch(
            "/api/v1/admin/courses/curso-imagen/",
            {"cover_image": _make_image()},
            format="multipart",
        )
        assert patch.status_code == 200
        assert patch.json()["data"]["cover_image_url"] is not None

    def test_create_recipe_lifetime_and_timed(self, staff_client, languages):
        lifetime = staff_client.post(
            "/api/v1/admin/recipes/",
            {
                "slug": "receta-lifetime",
                "price": "9.99",
                "access_type": "lifetime",
                "status": "published",
                "translations": [
                    {"language_code": "es", "title": "Receta lifetime", "description": ""},
                ],
            },
            format="json",
        )
        assert lifetime.status_code == 201

        timed = staff_client.post(
            "/api/v1/admin/recipes/",
            {
                "slug": "receta-timed",
                "price": "14.99",
                "access_type": "timed",
                "access_days": 365,
                "status": "published",
                "translations": [
                    {"language_code": "es", "title": "Receta timed", "description": ""},
                ],
            },
            format="json",
        )
        assert timed.status_code == 201

    def test_admin_requires_staff(self, api_client, languages):
        response = api_client.get("/api/v1/admin/courses/")
        assert response.status_code == 401

    def test_manage_languages(self, staff_client):
        response = staff_client.post(
            "/api/v1/admin/languages/",
            {"code": "fr", "name": "Français", "is_active": True},
            format="json",
        )
        assert response.status_code == 201

        deactivate = staff_client.patch(
            "/api/v1/admin/languages/fr/",
            {"is_active": False},
            format="json",
        )
        assert deactivate.status_code == 200

    def test_create_category_bilingual(self, staff_client, api_client, languages):
        response = staff_client.post(
            "/api/v1/admin/categories/",
            {
                "slug": "postres",
                "sort_order": 1,
                "translations": [
                    {"language_code": "es", "name": "Postres", "description": "Dulces"},
                    {"language_code": "en", "name": "Desserts", "description": "Sweets"},
                ],
            },
            format="json",
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert len(data["translations"]) == 2

        public = api_client.get("/api/v1/public/categories/?lang=es")
        assert public.status_code == 200
        slugs = [item["slug"] for item in public.json()["data"]]
        assert "postres" in slugs
