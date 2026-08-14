from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import UserAccount
from apps.catalog.models import Course
from apps.commerce.models import Order, Purchase
from apps.content.models import AccessGrant, LessonProgress
from apps.content.tasks import expire_access_grants_task


def _user_client(registered_user) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {registered_user['access']}")
    return client


def _grant(*, registered_user, course_id=None, recipe_id=None, expires_at=None, revoked=False):
    user = UserAccount.objects.get(pk=registered_user["id"])
    return AccessGrant.objects.create(
        user=user,
        course_id=course_id,
        recipe_id=recipe_id,
        expires_at=expires_at,
        is_revoked=revoked,
        source=AccessGrant.Source.PURCHASE,
    )


def _paid_purchase(*, registered_user, course=None, recipe=None, grant=None):
    user = UserAccount.objects.get(pk=registered_user["id"])
    order = Order.objects.create(
        user=user,
        status=Order.Status.PAID,
        total=Decimal("49.99"),
        currency="eur",
        paid_at=timezone.now(),
        customer_email=user.email,
    )
    return Purchase.objects.create(
        user=user,
        order=order,
        course=course,
        recipe=recipe,
        access_grant=grant,
    )


def _add_lesson(staff_client, course_slug="curso-pasta"):
    module = staff_client.post(
        f"/api/v1/admin/courses/{course_slug}/modules/",
        {
            "sort_order": 0,
            "translations": [{"language_code": "es", "title": "Introducción"}],
        },
        format="json",
    )
    assert module.status_code == 201, module.json()
    module_id = module.json()["data"]["id"]
    lesson = staff_client.post(
        f"/api/v1/admin/modules/{module_id}/lessons/",
        {
            "duration_seconds": 90,
            "translations": [{"language_code": "es", "title": "Bienvenida"}],
        },
        format="json",
    )
    assert lesson.status_code == 201, lesson.json()
    return lesson.json()["data"]


def _create_recipe(staff_client, *, slug, access_type="lifetime", access_days=None):
    payload = {
        "slug": slug,
        "price": "8.00",
        "status": "published",
        "access_type": access_type,
        "translations": [{"language_code": "es", "title": slug, "description": ""}],
    }
    if access_days is not None:
        payload["access_days"] = access_days
    created = staff_client.post("/api/v1/admin/recipes/", payload, format="json")
    assert created.status_code == 201, created.json()
    return created.json()["data"]


@pytest.mark.django_db
class TestMePurchasesAndLibrary:
    def test_purchases_and_active_courses(self, published_course, registered_user):
        grant = _grant(
            registered_user=registered_user,
            course_id=published_course["id"],
            expires_at=timezone.now() + timedelta(days=365),
        )
        course = Course.objects.get(pk=published_course["id"])
        _paid_purchase(registered_user=registered_user, course=course, grant=grant)
        client = _user_client(registered_user)

        purchases = client.get("/api/v1/me/purchases/?lang=es")
        assert purchases.status_code == 200
        row = purchases.json()["results"][0]
        assert row["product_type"] == "course"
        assert row["title"] == "Curso de Pasta"
        assert row["is_active"] is True
        assert row["is_lifetime"] is False
        assert row["expires_at"] is not None

        listing = client.get("/api/v1/me/courses/?lang=es")
        assert listing.status_code == 200
        assert listing.json()["results"][0]["title"] == "Curso de Pasta"
        assert listing.json()["results"][0]["is_active"] is True

    def test_expired_course_hidden_from_library(self, published_course, registered_user):
        _grant(
            registered_user=registered_user,
            course_id=published_course["id"],
            expires_at=timezone.now() - timedelta(days=1),
        )
        client = _user_client(registered_user)
        listing = client.get("/api/v1/me/courses/")
        assert listing.json()["count"] == 0

    def test_lifetime_recipe_listed(self, staff_client, languages, registered_user):
        recipe = _create_recipe(staff_client, slug="receta-life", access_type="lifetime")
        _grant(registered_user=registered_user, recipe_id=recipe["id"], expires_at=None)
        client = _user_client(registered_user)
        listing = client.get("/api/v1/me/recipes/?lang=es")
        assert listing.status_code == 200
        row = listing.json()["results"][0]
        assert row["is_lifetime"] is True
        assert row["expires_at"] is None
        assert row["access_type"] == "lifetime"


@pytest.mark.django_db
class TestMeProgress:
    def test_complete_view_and_percent(self, staff_client, published_course, registered_user):
        _grant(
            registered_user=registered_user,
            course_id=published_course["id"],
            expires_at=timezone.now() + timedelta(days=30),
        )
        lesson = _add_lesson(staff_client)
        client = _user_client(registered_user)

        viewed = client.post(f"/api/v1/me/lessons/{lesson['id']}/view/")
        assert viewed.status_code == 200
        assert viewed.json()["data"]["completed"] is False
        assert viewed.json()["data"]["last_viewed_at"] is not None

        done = client.post(f"/api/v1/me/lessons/{lesson['id']}/complete/")
        assert done.status_code == 200
        assert done.json()["data"]["completed"] is True
        assert LessonProgress.objects.filter(
            user_id=registered_user["id"], lesson_id=lesson["id"], completed=True
        ).exists()

        progress = client.get(f"/api/v1/me/progress/{published_course['id']}/?lang=es")
        assert progress.status_code == 200
        data = progress.json()["data"]
        assert data["total_lessons"] == 1
        assert data["completed_lessons"] == 1
        assert data["percent"] == 100
        assert data["continue_lesson"]["id"] == lesson["id"]
        assert data["lessons"][0]["title"] == "Bienvenida"

        courses = client.get("/api/v1/me/courses/")
        assert courses.json()["results"][0]["continue_lesson"]["id"] == lesson["id"]

    def test_progress_forbidden_when_expired(self, staff_client, published_course, registered_user):
        _grant(
            registered_user=registered_user,
            course_id=published_course["id"],
            expires_at=timezone.now() - timedelta(hours=1),
        )
        _add_lesson(staff_client)
        client = _user_client(registered_user)
        response = client.get(f"/api/v1/me/progress/{published_course['id']}/")
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "ACCESS_EXPIRED"

    def test_complete_requires_access(self, staff_client, published_course, registered_user):
        lesson = _add_lesson(staff_client)
        client = _user_client(registered_user)
        response = client.post(f"/api/v1/me/lessons/{lesson['id']}/complete/")
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "ACCESS_DENIED"


@pytest.mark.django_db
class TestExpireAccessGrantsTask:
    def test_counts_expired_grants(self, published_course, registered_user):
        _grant(
            registered_user=registered_user,
            course_id=published_course["id"],
            expires_at=timezone.now() - timedelta(days=2),
        )
        result = expire_access_grants_task()
        assert result["expired_count"] == 1
