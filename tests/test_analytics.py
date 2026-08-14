from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.accounts.models import UserAccount
from apps.commerce.models import Order, OrderItem


def _paid_order(*, user, total, paid_at, title="Curso de Pasta", course=None, recipe=None):
    order = Order.objects.create(
        user=user,
        status=Order.Status.PAID,
        total=Decimal(total),
        currency="eur",
        paid_at=paid_at,
        customer_email=user.email,
    )
    OrderItem.objects.create(
        order=order,
        course=course,
        recipe=recipe,
        title=title,
        unit_price=Decimal(total),
    )
    return order


@pytest.mark.django_db
class TestAdminDashboard:
    def test_requires_staff(self, registered_user):
        from rest_framework.test import APIClient

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {registered_user['access']}")
        response = client.get("/api/v1/admin/dashboard/")
        assert response.status_code == 403

    def test_empty_dashboard(self, staff_client):
        response = staff_client.get("/api/v1/admin/dashboard/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["totals"]["revenue_all_time"] == "0.00"
        assert data["totals"]["orders_paid_all_time"] == 0
        assert data["recent_orders"] == []
        assert data["top_products"] == []

    def test_aggregates_paid_orders(self, staff_client, published_course, registered_user):
        user = UserAccount.objects.get(pk=registered_user["id"])
        from apps.catalog.models import Course

        course = Course.objects.get(pk=published_course["id"])
        now = timezone.now()
        _paid_order(user=user, total="49.99", paid_at=now, course=course)
        _paid_order(
            user=user,
            total="20.00",
            paid_at=now - timedelta(days=40),
            title="Viejo",
            course=course,
        )
        Order.objects.create(
            user=user,
            status=Order.Status.PENDING,
            total=Decimal("10.00"),
            customer_email=user.email,
        )

        month = staff_client.get("/api/v1/admin/dashboard/?period=month")
        assert month.status_code == 200
        totals = month.json()["data"]["totals"]
        assert totals["revenue_all_time"] == "69.99"
        assert totals["orders_paid_all_time"] == 2
        assert totals["orders_paid_period"] == 1
        assert totals["revenue_period"] == "49.99"
        assert totals["orders_pending"] == 1
        assert totals["customers_with_purchases"] == 1

        recent = month.json()["data"]["recent_orders"]
        assert len(recent) == 2
        assert recent[0]["items"][0]["title"] == "Curso de Pasta"

        top = month.json()["data"]["top_products"]
        assert top[0]["product_type"] == "course"
        assert top[0]["units"] == 1
        assert top[0]["revenue"] == "49.99"

        all_time = staff_client.get("/api/v1/admin/dashboard/?period=all")
        assert all_time.json()["data"]["totals"]["revenue_period"] == "69.99"
        assert all_time.json()["data"]["top_products"][0]["units"] == 2

    def test_invalid_period(self, staff_client):
        response = staff_client.get("/api/v1/admin/dashboard/?period=year")
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "PERIOD_INVALID"

    def test_revenue_series(self, staff_client, published_course, registered_user):
        user = UserAccount.objects.get(pk=registered_user["id"])
        from apps.catalog.models import Course

        course = Course.objects.get(pk=published_course["id"])
        _paid_order(user=user, total="49.99", paid_at=timezone.now(), course=course)

        response = staff_client.get("/api/v1/admin/dashboard/revenue/?granularity=day&days=7")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["granularity"] == "day"
        assert data["currency"] == "eur"
        assert any(point["orders"] == 1 and point["revenue"] == "49.99" for point in data["points"])

    def test_revenue_invalid_granularity(self, staff_client):
        response = staff_client.get("/api/v1/admin/dashboard/revenue/?granularity=hour")
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "GRANULARITY_INVALID"
