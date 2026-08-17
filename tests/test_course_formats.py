import json
from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import UserAccount
from apps.catalog.models import Course
from apps.commerce.models import Order, Purchase
from apps.content.models import AccessGrant


def _user_client(registered_user) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {registered_user['access']}")
    return client


def _pdf(name: str = "guia.pdf") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, b"%PDF-1.4 test-resource", content_type="application/pdf")


def _translations_payload():
    return json.dumps(
        [
            {
                "language_code": "es",
                "title": "Guía de pasta",
                "description": "PDF complementario",
            }
        ]
    )


def _in_person_payload(slug: str = "taller-madrid"):
    return {
        "slug": slug,
        "price": "79.00",
        "format": "in_person",
        "event_starts_at": "2026-09-15T18:00:00Z",
        "event_address": "Calle Mayor 1, Madrid",
        "maps_url": "https://maps.google.com/?q=Calle+Mayor+1+Madrid",
        "status": "published",
        "translations": [
            {
                "language_code": "es",
                "title": "Taller de pasta en Madrid",
                "description": "Clase presencial",
            }
        ],
    }


def _grant(*, registered_user, course_id, expires_at=None):
    user = UserAccount.objects.get(pk=registered_user["id"])
    return AccessGrant.objects.create(
        user=user,
        course_id=course_id,
        expires_at=expires_at,
        source=AccessGrant.Source.PURCHASE,
    )


def _paid_purchase(*, registered_user, course):
    user = UserAccount.objects.get(pk=registered_user["id"])
    order = Order.objects.create(
        user=user,
        status=Order.Status.PAID,
        total=Decimal("79.00"),
        currency="eur",
        paid_at=timezone.now(),
        customer_email=user.email,
    )
    grant = AccessGrant.objects.create(
        user=user,
        course=course,
        expires_at=timezone.now() + timedelta(days=365),
        source=AccessGrant.Source.PURCHASE,
    )
    return Purchase.objects.create(
        user=user,
        order=order,
        course=course,
        access_grant=grant,
    )


@pytest.mark.django_db
class TestInPersonCourses:
    def test_create_and_public_detail(self, staff_client, api_client, languages):
        created = staff_client.post(
            "/api/v1/admin/courses/",
            _in_person_payload(),
            format="json",
        )
        assert created.status_code == 201, created.json()
        data = created.json()["data"]
        assert data["format"] == "in_person"
        assert data["event_address"] == "Calle Mayor 1, Madrid"
        assert "maps.google.com" in data["maps_url"]

        public = api_client.get("/api/v1/public/courses/taller-madrid/?lang=es")
        assert public.status_code == 200
        body = public.json()["data"]
        assert body["format"] == "in_person"
        assert body["modules"] == []
        assert body["event_starts_at"] is not None

        listing = api_client.get("/api/v1/public/courses/?lang=es&course_format=in_person")
        slugs = [item["slug"] for item in listing.json()["results"]]
        assert "taller-madrid" in slugs

        online_only = api_client.get("/api/v1/public/courses/?lang=es&course_format=online")
        online_slugs = [item["slug"] for item in online_only.json()["results"]]
        assert "taller-madrid" not in online_slugs

    def test_requires_event_fields(self, staff_client, languages):
        payload = _in_person_payload("taller-incompleto")
        payload.pop("maps_url")
        response = staff_client.post("/api/v1/admin/courses/", payload, format="json")
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "IN_PERSON_EVENT_REQUIRED"

    def test_cannot_add_modules_or_resources(self, staff_client, languages):
        created = staff_client.post(
            "/api/v1/admin/courses/",
            _in_person_payload(),
            format="json",
        )
        assert created.status_code == 201

        module = staff_client.post(
            "/api/v1/admin/courses/taller-madrid/modules/",
            {
                "sort_order": 0,
                "translations": [{"language_code": "es", "title": "No aplica"}],
            },
            format="json",
        )
        assert module.status_code == 422
        assert module.json()["error"]["code"] == "IN_PERSON_NO_CURRICULUM"

        resource = staff_client.post(
            "/api/v1/admin/courses/taller-madrid/resources/",
            {"file": _pdf(), "translations": _translations_payload()},
            format="multipart",
        )
        assert resource.status_code == 422
        assert resource.json()["error"]["code"] == "IN_PERSON_NO_RESOURCES"

    def test_cannot_switch_online_with_modules(self, staff_client, published_course):
        module = staff_client.post(
            "/api/v1/admin/courses/curso-pasta/modules/",
            {
                "sort_order": 0,
                "translations": [{"language_code": "es", "title": "Intro"}],
            },
            format="json",
        )
        assert module.status_code == 201

        response = staff_client.patch(
            "/api/v1/admin/courses/curso-pasta/",
            {
                "format": "in_person",
                "event_starts_at": "2026-09-15T18:00:00Z",
                "event_address": "Calle Mayor 1",
                "maps_url": "https://maps.google.com/?q=Madrid",
            },
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "IN_PERSON_HAS_CONTENT"

    def test_admin_purchase_list(self, staff_client, languages, registered_user):
        created = staff_client.post(
            "/api/v1/admin/courses/",
            _in_person_payload(),
            format="json",
        )
        course = Course.objects.get(pk=created.json()["data"]["id"])
        _paid_purchase(registered_user=registered_user, course=course)

        response = staff_client.get("/api/v1/admin/courses/taller-madrid/purchases/")
        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["user"]["email"] == "user@recetario.local"
        assert results[0]["order_id"]
        assert results[0]["is_lifetime"] is False


@pytest.mark.django_db
class TestCourseResources:
    def test_admin_upload_and_me_download(self, staff_client, published_course, registered_user):
        created = staff_client.post(
            "/api/v1/admin/courses/curso-pasta/resources/",
            {"file": _pdf(), "translations": _translations_payload()},
            format="multipart",
        )
        assert created.status_code == 201, created.json()
        resource = created.json()["data"]
        assert resource["kind"] == "pdf"
        assert resource["original_name"] == "guia.pdf"
        resource_id = resource["id"]
        course_id = published_course["id"]

        listing = staff_client.get("/api/v1/admin/courses/curso-pasta/resources/")
        assert listing.status_code == 200
        assert listing.json()["data"][0]["id"] == resource_id

        client = _user_client(registered_user)
        denied = client.get(f"/api/v1/me/courses/{course_id}/resources/")
        assert denied.status_code == 403
        assert denied.json()["error"]["code"] == "ACCESS_DENIED"

        _grant(registered_user=registered_user, course_id=course_id)
        allowed = client.get(f"/api/v1/me/courses/{course_id}/resources/?lang=es")
        assert allowed.status_code == 200
        rows = allowed.json()["data"]["resources"]
        assert len(rows) == 1
        assert rows[0]["title"] == "Guía de pasta"
        assert rows[0]["kind"] == "pdf"
        assert f"/resources/{resource_id}/file/" in rows[0]["download_url"]

        download = client.get(f"/api/v1/me/courses/{course_id}/resources/{resource_id}/file/")
        assert download.status_code == 200
        assert b"".join(download.streaming_content) == b"%PDF-1.4 test-resource"

        staff_file = staff_client.get(f"/api/v1/admin/resources/{resource_id}/file/")
        assert staff_file.status_code == 200
        assert b"".join(staff_file.streaming_content) == b"%PDF-1.4 test-resource"

    def test_inactive_hidden_from_me(self, staff_client, published_course, registered_user):
        created = staff_client.post(
            "/api/v1/admin/courses/curso-pasta/resources/",
            {
                "file": _pdf("oculto.pdf"),
                "is_active": False,
                "translations": _translations_payload(),
            },
            format="multipart",
        )
        assert created.status_code == 201
        resource_id = created.json()["data"]["id"]
        course_id = published_course["id"]
        _grant(registered_user=registered_user, course_id=course_id)

        client = _user_client(registered_user)
        listing = client.get(f"/api/v1/me/courses/{course_id}/resources/")
        assert listing.json()["data"]["resources"] == []

        download = client.get(f"/api/v1/me/courses/{course_id}/resources/{resource_id}/file/")
        assert download.status_code == 404
