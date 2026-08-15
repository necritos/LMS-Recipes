import hashlib
import time
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import UserAccount
from apps.content.models import AccessGrant

BUNNY_TOKEN_KEY = "test-bunny-token-key"
BUNNY_LIBRARY = "12345"
VIDEO_ID = "aaaa-bbbb-cccc"


def _user_client(registered_user) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {registered_user['access']}")
    return client


def _enable_bunny(staff_client, ttl=3600):
    response = staff_client.patch(
        "/api/v1/admin/site/bunny/",
        {
            "bunny_enabled": True,
            "bunny_library_id": BUNNY_LIBRARY,
            "bunny_cdn_hostname": "https://vz-demo.b-cdn.net/path",
            "bunny_token_key": BUNNY_TOKEN_KEY,
            "bunny_api_key": "stream-api-key",
            "bunny_token_ttl_seconds": ttl,
        },
        format="json",
    )
    assert response.status_code == 200, response.json()
    return response.json()["data"]


def _add_module_and_lesson(staff_client, course_slug, video_id=VIDEO_ID):
    module = staff_client.post(
        f"/api/v1/admin/courses/{course_slug}/modules/",
        {
            "sort_order": 0,
            "translations": [
                {
                    "language_code": "es",
                    "title": "Introducción",
                    "description": "Descripción del módulo ES",
                },
                {
                    "language_code": "en",
                    "title": "Introduction",
                    "description": "Module description EN",
                },
            ],
        },
        format="json",
    )
    assert module.status_code == 201, module.json()
    module_id = module.json()["data"]["id"]
    lesson = staff_client.post(
        f"/api/v1/admin/modules/{module_id}/lessons/",
        {
            "bunny_video_id": video_id,
            "duration_seconds": 90,
            "translations": [
                {
                    "language_code": "es",
                    "title": "Bienvenida",
                    "description": "Resumen lección",
                    "content_html": "<p>Contenido HTML ES</p>",
                },
                {
                    "language_code": "en",
                    "title": "Welcome",
                    "description": "Lesson summary",
                    "content_html": "<p>HTML content EN</p>",
                },
            ],
        },
        format="json",
    )
    assert lesson.status_code == 201, lesson.json()
    return module.json()["data"], lesson.json()["data"]


def _grant(*, registered_user, course_id=None, recipe_id=None, expires_at=None, revoked=False):
    user = UserAccount.objects.get(pk=registered_user["id"])
    return AccessGrant.objects.create(
        user=user,
        course_id=course_id,
        recipe_id=recipe_id,
        expires_at=expires_at,
        is_revoked=revoked,
    )


@pytest.mark.django_db
class TestAdminBunnySettings:
    def test_get_does_not_expose_secrets(self, staff_client):
        _enable_bunny(staff_client)
        response = staff_client.get("/api/v1/admin/site/bunny/")
        data = response.json()["data"]
        assert data["bunny_enabled"] is True
        assert data["bunny_configured"] is True
        assert data["bunny_api_configured"] is True
        assert data["bunny_cdn_hostname"] == "vz-demo.b-cdn.net"
        assert "bunny_token_key" not in data
        assert "bunny_api_key" not in data
        assert BUNNY_TOKEN_KEY not in str(data)

    def test_enable_requires_library_and_token(self, staff_client):
        response = staff_client.patch(
            "/api/v1/admin/site/bunny/",
            {"bunny_enabled": True, "bunny_library_id": "1"},
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "BUNNY_CONFIG_INCOMPLETE"

    def test_blank_secret_keeps_previous(self, staff_client):
        _enable_bunny(staff_client)
        patched = staff_client.patch(
            "/api/v1/admin/site/bunny/",
            {"bunny_token_key": "", "bunny_token_ttl_seconds": 1800},
            format="json",
        )
        assert patched.status_code == 200
        assert patched.json()["data"]["bunny_configured"] is True
        assert patched.json()["data"]["bunny_token_ttl_seconds"] == 1800


@pytest.mark.django_db
class TestAdminCurriculum:
    def test_create_module_and_lesson(self, staff_client, published_course):
        module, lesson = _add_module_and_lesson(staff_client, "curso-pasta")
        assert module["translations"][0]["title"] in {"Introducción", "Introduction"}
        assert any(t.get("description") for t in module["translations"])
        assert lesson["bunny_video_id"] == VIDEO_ID
        assert any(t.get("content_html") for t in lesson["translations"])

        listing = staff_client.get("/api/v1/admin/courses/curso-pasta/modules/")
        assert listing.status_code == 200
        assert len(listing.json()["data"]) == 1
        assert listing.json()["data"][0]["lessons"][0]["bunny_video_id"] == VIDEO_ID

    def test_assign_recipe_video(self, staff_client, languages):
        created = staff_client.post(
            "/api/v1/admin/recipes/",
            {
                "slug": "receta-video",
                "price": "9.99",
                "status": "published",
                "bunny_video_id": VIDEO_ID,
                "translations": [
                    {"language_code": "es", "title": "Video receta", "description": ""}
                ],
            },
            format="json",
        )
        assert created.status_code == 201
        assert created.json()["data"]["bunny_video_id"] == VIDEO_ID


@pytest.mark.django_db
class TestPublicCurriculum:
    def test_course_detail_lists_modules_without_video_id(
        self, api_client, staff_client, published_course
    ):
        _add_module_and_lesson(staff_client, "curso-pasta")
        response = api_client.get("/api/v1/public/courses/curso-pasta/?lang=es")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["modules"][0]["title"] == "Introducción"
        assert data["modules"][0]["description"] == "Descripción del módulo ES"
        assert data["modules"][0]["lessons"][0]["title"] == "Bienvenida"
        assert data["modules"][0]["lessons"][0]["description"] == "Resumen lección"
        assert "bunny_video_id" not in data["modules"][0]["lessons"][0]
        assert "content_html" not in data["modules"][0]["lessons"][0]


@pytest.mark.django_db
class TestMeVideoAccess:
    def test_lessons_with_signed_url(self, staff_client, published_course, registered_user):
        _enable_bunny(staff_client)
        _add_module_and_lesson(staff_client, "curso-pasta")
        _grant(
            registered_user=registered_user,
            course_id=published_course["id"],
            expires_at=timezone.now() + timedelta(days=365),
        )
        client = _user_client(registered_user)
        response = client.get(f"/api/v1/me/courses/{published_course['id']}/lessons/?lang=es")
        assert response.status_code == 200, response.json()
        lesson = response.json()["data"]["modules"][0]["lessons"][0]
        assert lesson["title"] == "Bienvenida"
        assert lesson["description"] == "Resumen lección"
        assert lesson["content_html"] == "<p>Contenido HTML ES</p>"
        assert "bunny_video_id" not in lesson
        module = response.json()["data"]["modules"][0]
        assert module["description"] == "Descripción del módulo ES"
        video = lesson["video"]
        assert BUNNY_LIBRARY in video["signed_video_url"]
        assert "vz-demo.b-cdn.net" in video["hls_url"]
        qs = parse_qs(urlparse(video["signed_video_url"]).query)
        expires = int(qs["expires"][0])
        token = qs["token"][0]
        expected = hashlib.sha256(f"{BUNNY_TOKEN_KEY}{VIDEO_ID}{expires}".encode()).hexdigest()
        assert token == expected
        assert abs(expires - (time.time() + 3600)) < 10

    def test_denied_without_grant(self, staff_client, published_course, registered_user):
        _enable_bunny(staff_client)
        _add_module_and_lesson(staff_client, "curso-pasta")
        client = _user_client(registered_user)
        response = client.get(f"/api/v1/me/courses/{published_course['id']}/lessons/")
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "ACCESS_DENIED"

    def test_expired_grant(self, staff_client, published_course, registered_user):
        _enable_bunny(staff_client)
        _add_module_and_lesson(staff_client, "curso-pasta")
        _grant(
            registered_user=registered_user,
            course_id=published_course["id"],
            expires_at=timezone.now() - timedelta(days=1),
        )
        client = _user_client(registered_user)
        response = client.get(f"/api/v1/me/courses/{published_course['id']}/lessons/")
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "ACCESS_EXPIRED"

    def test_unauthenticated(self, published_course):
        response = APIClient().get(f"/api/v1/me/courses/{published_course['id']}/lessons/")
        assert response.status_code == 401

    def test_recipe_video(self, staff_client, languages, registered_user):
        _enable_bunny(staff_client)
        created = staff_client.post(
            "/api/v1/admin/recipes/",
            {
                "slug": "tiramisu-video",
                "price": "8.00",
                "status": "published",
                "bunny_video_id": VIDEO_ID,
                "translations": [{"language_code": "es", "title": "Tiramisú", "description": ""}],
            },
            format="json",
        )
        recipe_id = created.json()["data"]["id"]
        _grant(
            registered_user=registered_user,
            recipe_id=recipe_id,
            expires_at=None,
        )
        client = _user_client(registered_user)
        response = client.get(f"/api/v1/me/recipes/{recipe_id}/video/")
        assert response.status_code == 200
        video = response.json()["data"]["video"]
        assert "signed_video_url" in video
        assert "bunny_video_id" not in response.json()["data"]

    def test_recipe_detail_ingredients_only_with_access(
        self, staff_client, api_client, languages, registered_user
    ):
        _enable_bunny(staff_client)
        created = staff_client.post(
            "/api/v1/admin/recipes/",
            {
                "slug": "tiramisu-full",
                "price": "8.00",
                "status": "published",
                "bunny_video_id": VIDEO_ID,
                "translations": [
                    {
                        "language_code": "es",
                        "title": "Tiramisú",
                        "description": "Teaser público",
                        "ingredients_html": "<ul><li>Mascarpone</li></ul>",
                        "preparation_html": "<ol><li>Batir</li></ol>",
                    }
                ],
            },
            format="json",
        )
        assert created.status_code == 201, created.json()
        recipe = created.json()["data"]
        recipe_id = recipe["id"]

        public = api_client.get("/api/v1/public/recipes/tiramisu-full/?lang=es")
        assert public.status_code == 200
        public_data = public.json()["data"]
        assert public_data["description"] == "Teaser público"
        assert "ingredients_html" not in public_data
        assert "preparation_html" not in public_data

        denied = _user_client(registered_user).get(f"/api/v1/me/recipes/{recipe_id}/?lang=es")
        assert denied.status_code == 403

        _grant(registered_user=registered_user, recipe_id=recipe_id, expires_at=None)
        detail = _user_client(registered_user).get(f"/api/v1/me/recipes/{recipe_id}/?lang=es")
        assert detail.status_code == 200, detail.json()
        data = detail.json()["data"]
        assert data["ingredients_html"] == "<ul><li>Mascarpone</li></ul>"
        assert data["preparation_html"] == "<ol><li>Batir</li></ol>"
        assert data["video"]["signed_video_url"]

    def test_bunny_not_configured(self, staff_client, published_course, registered_user):
        _add_module_and_lesson(staff_client, "curso-pasta")
        _grant(
            registered_user=registered_user,
            course_id=published_course["id"],
            expires_at=timezone.now() + timedelta(days=30),
        )
        client = _user_client(registered_user)
        response = client.get(f"/api/v1/me/courses/{published_course['id']}/lessons/")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "BUNNY_NOT_CONFIGURED"
