from types import SimpleNamespace

import pytest
from django.core import mail
from rest_framework.test import APIClient

from apps.commerce.models import Order, PaymentAttempt, Purchase, StripeEvent
from apps.content.models import AccessGrant

STRIPE_SECRET = "sk_test_51fake00000000000000000000000000000000"
WEBHOOK_SECRET = "whsec_test_secret_value"


def _user_client(registered_user) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {registered_user['access']}")
    return client


def _enable_stripe(staff_client):
    response = staff_client.patch(
        "/api/v1/admin/site/stripe/",
        {
            "stripe_enabled": True,
            "stripe_mode": "test",
            "stripe_secret_key": STRIPE_SECRET,
            "stripe_publishable_key": "pk_test_public",
            "stripe_webhook_secret": WEBHOOK_SECRET,
            "stripe_success_url": "https://petralicious.sk/checkout/success",
            "stripe_cancel_url": "https://petralicious.sk/checkout/cancel",
            "stripe_currency": "eur",
        },
        format="json",
    )
    assert response.status_code == 200, response.json()
    return response.json()["data"]


@pytest.mark.django_db
class TestAdminStripeSettings:
    def test_get_does_not_expose_secrets(self, staff_client):
        _enable_stripe(staff_client)
        data = staff_client.get("/api/v1/admin/site/stripe/").json()["data"]
        assert data["stripe_enabled"] is True
        assert data["stripe_configured"] is True
        assert data["stripe_webhook_configured"] is True
        assert data["stripe_publishable_key"] == "pk_test_public"
        assert "stripe_secret_key" not in data
        assert "stripe_webhook_secret" not in data
        assert STRIPE_SECRET not in str(data)

    def test_enable_requires_urls_and_secret(self, staff_client):
        response = staff_client.patch(
            "/api/v1/admin/site/stripe/",
            {"stripe_enabled": True, "stripe_mode": "test"},
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "STRIPE_CONFIG_INCOMPLETE"

    def test_key_must_match_mode(self, staff_client):
        response = staff_client.patch(
            "/api/v1/admin/site/stripe/",
            {
                "stripe_enabled": True,
                "stripe_mode": "live",
                "stripe_secret_key": STRIPE_SECRET,
                "stripe_success_url": "https://x/ok",
                "stripe_cancel_url": "https://x/ko",
            },
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "STRIPE_KEY_MODE_MISMATCH"


@pytest.mark.django_db
class TestCart:
    def test_add_list_and_remove(self, published_course, registered_user):
        client = _user_client(registered_user)
        added = client.post(
            "/api/v1/me/cart/",
            {"course_id": published_course["id"]},
            format="json",
        )
        assert added.status_code == 201
        data = added.json()["data"]
        assert data["total"] == "49.99"
        assert data["items"][0]["title"] == "Curso de Pasta"
        item_id = data["items"][0]["id"]

        duplicate = client.post(
            "/api/v1/me/cart/",
            {"course_id": published_course["id"]},
            format="json",
        )
        assert duplicate.status_code == 409

        listing = client.get("/api/v1/me/cart/?lang=en")
        assert listing.json()["data"]["items"][0]["title"] == "Pasta Course"

        removed = client.delete(f"/api/v1/me/cart/items/{item_id}/")
        assert removed.status_code == 200
        assert removed.json()["data"]["items"] == []

    def test_requires_one_product(self, registered_user):
        client = _user_client(registered_user)
        response = client.post("/api/v1/me/cart/", {}, format="json")
        assert response.status_code == 422


@pytest.mark.django_db
class TestCheckoutAndWebhook:
    def test_empty_cart(self, staff_client, registered_user):
        _enable_stripe(staff_client)
        client = _user_client(registered_user)
        response = client.post("/api/v1/checkout/create-session/", {}, format="json")
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "CART_EMPTY"

    def test_stripe_not_configured(self, published_course, registered_user):
        client = _user_client(registered_user)
        client.post("/api/v1/me/cart/", {"course_id": published_course["id"]}, format="json")
        response = client.post("/api/v1/checkout/create-session/", {}, format="json")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "STRIPE_NOT_CONFIGURED"

    def test_checkout_and_webhook_grants_access(
        self, staff_client, published_course, registered_user, monkeypatch
    ):
        _enable_stripe(staff_client)
        client = _user_client(registered_user)
        client.post("/api/v1/me/cart/", {"course_id": published_course["id"]}, format="json")

        monkeypatch.setattr(
            "apps.commerce.services.checkout_service.create_stripe_checkout_session",
            lambda **kwargs: SimpleNamespace(
                id="cs_test_123", url="https://checkout.stripe.com/c/pay/cs_test_123"
            ),
        )
        checkout = client.post("/api/v1/checkout/create-session/", {"lang": "es"}, format="json")
        assert checkout.status_code == 200, checkout.json()
        body = checkout.json()["data"]
        assert body["checkout_url"].startswith("https://checkout.stripe.com/")
        order_id = body["order_id"]

        event = {
            "id": "evt_test_1",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "object": "checkout.session",
                    "payment_intent": "pi_test_1",
                    "metadata": {"order_id": order_id, "user_id": registered_user["id"]},
                }
            },
        }
        monkeypatch.setattr(
            "apps.commerce.services.webhook_service.construct_stripe_event",
            lambda **kwargs: event,
        )
        webhook = APIClient().post(
            "/api/v1/webhooks/stripe/",
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=test",
        )
        assert webhook.status_code == 200, webhook.json()
        assert webhook.json()["data"]["status"] == "processed"

        order = Order.objects.get(pk=order_id)
        assert order.status == Order.Status.PAID
        assert AccessGrant.objects.filter(
            user_id=registered_user["id"], course_id=published_course["id"]
        ).exists()
        assert Purchase.objects.filter(order=order).count() == 1
        assert any("compra" in message.subject.lower() for message in mail.outbox)

        cart = client.get("/api/v1/me/cart/").json()["data"]
        assert cart["items"] == []

        again = APIClient().post(
            "/api/v1/webhooks/stripe/",
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=test",
        )
        assert again.json()["data"]["status"] == "duplicate"
        assert StripeEvent.objects.count() == 1

    def test_checkout_uses_frontend_redirect_urls(
        self, staff_client, published_course, registered_user, monkeypatch
    ):
        _enable_stripe(staff_client)
        client = _user_client(registered_user)
        client.post("/api/v1/me/cart/", {"course_id": published_course["id"]}, format="json")
        captured = {}

        def _fake_session(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(id="cs_test_urls", url="https://checkout.stripe.com/c/pay/x")

        monkeypatch.setattr(
            "apps.commerce.services.checkout_service.create_stripe_checkout_session",
            _fake_session,
        )
        response = client.post(
            "/api/v1/checkout/create-session/",
            {
                "lang": "es",
                "stripe_success_url": "https://petralicious.com/checkout/success",
                "stripe_cancel_url": "https://www.petralicious.com/cart",
            },
            format="json",
        )
        assert response.status_code == 200, response.json()
        params = captured["params"]
        assert params["success_url"].startswith("https://petralicious.com/checkout/success")
        assert "session_id={CHECKOUT_SESSION_ID}" in params["success_url"]
        assert params["cancel_url"] == "https://www.petralicious.com/cart"

    def test_checkout_rejects_foreign_redirect(
        self, staff_client, published_course, registered_user
    ):
        _enable_stripe(staff_client)
        client = _user_client(registered_user)
        client.post("/api/v1/me/cart/", {"course_id": published_course["id"]}, format="json")
        response = client.post(
            "/api/v1/checkout/create-session/",
            {
                "stripe_success_url": "https://evil.example/phish",
                "stripe_cancel_url": "https://petralicious.sk/checkout/cancel",
            },
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "CHECKOUT_REDIRECT_NOT_ALLOWED"

    def test_webhook_rejects_bad_signature(self, staff_client):
        _enable_stripe(staff_client)
        response = APIClient().post(
            "/api/v1/webhooks/stripe/",
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=deadbeef",
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "STRIPE_SIGNATURE_INVALID"

    def test_records_started_and_succeeded_attempts(
        self, staff_client, published_course, registered_user, monkeypatch
    ):
        _enable_stripe(staff_client)
        order_id = _checkout_order(published_course, registered_user, monkeypatch)
        assert PaymentAttempt.objects.filter(
            order_id=order_id, outcome=PaymentAttempt.Outcome.STARTED
        ).exists()

        _post_webhook(
            monkeypatch,
            {
                "id": "evt_ok",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": "cs_test_123",
                        "object": "checkout.session",
                        "payment_intent": "pi_ok",
                        "metadata": {"order_id": order_id},
                    }
                },
            },
        )
        outcomes = list(
            PaymentAttempt.objects.filter(order_id=order_id)
            .order_by("created_at")
            .values_list("outcome", flat=True)
        )
        assert outcomes == [
            PaymentAttempt.Outcome.STARTED,
            PaymentAttempt.Outcome.SUCCEEDED,
        ]

    def test_records_failed_attempt_with_stripe_message(
        self, staff_client, published_course, registered_user, monkeypatch
    ):
        _enable_stripe(staff_client)
        order_id = _checkout_order(published_course, registered_user, monkeypatch)
        _post_webhook(
            monkeypatch,
            {
                "id": "evt_fail",
                "type": "payment_intent.payment_failed",
                "data": {
                    "object": {
                        "id": "pi_fail",
                        "object": "payment_intent",
                        "metadata": {"order_id": order_id},
                        "last_payment_error": {
                            "code": "card_declined",
                            "decline_code": "insufficient_funds",
                            "message": "Your card has insufficient funds.",
                        },
                    }
                },
            },
        )
        order = Order.objects.get(pk=order_id)
        assert order.status == Order.Status.FAILED
        attempt = PaymentAttempt.objects.get(order=order, outcome=PaymentAttempt.Outcome.FAILED)
        assert attempt.failure_code == "insufficient_funds"
        assert "insufficient funds" in attempt.failure_message.lower()

    def test_expired_session_marks_order_canceled(
        self, staff_client, published_course, registered_user, monkeypatch
    ):
        _enable_stripe(staff_client)
        order_id = _checkout_order(published_course, registered_user, monkeypatch)
        _post_webhook(
            monkeypatch,
            {
                "id": "evt_exp",
                "type": "checkout.session.expired",
                "data": {
                    "object": {
                        "id": "cs_test_123",
                        "object": "checkout.session",
                        "metadata": {"order_id": order_id},
                    }
                },
            },
        )
        order = Order.objects.get(pk=order_id)
        assert order.status == Order.Status.CANCELED
        assert PaymentAttempt.objects.filter(
            order=order, outcome=PaymentAttempt.Outcome.EXPIRED
        ).exists()


@pytest.mark.django_db
class TestAdminPayments:
    def test_requires_staff(self, api_client, registered_user):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {registered_user['access']}")
        response = api_client.get("/api/v1/admin/payments/")
        assert response.status_code == 403

    def test_list_filter_and_detail(
        self, staff_client, published_course, registered_user, monkeypatch
    ):
        _enable_stripe(staff_client)
        order_id = _checkout_order(published_course, registered_user, monkeypatch)
        _post_webhook(
            monkeypatch,
            {
                "id": "evt_fail_admin",
                "type": "payment_intent.payment_failed",
                "data": {
                    "object": {
                        "id": "pi_fail_admin",
                        "object": "payment_intent",
                        "metadata": {"order_id": order_id},
                        "last_payment_error": {
                            "decline_code": "generic_decline",
                            "message": "Your card was declined.",
                        },
                    }
                },
            },
        )

        listing = staff_client.get("/api/v1/admin/payments/")
        assert listing.status_code == 200
        body = listing.json()
        assert body["count"] == 2
        outcomes = {row["outcome"] for row in body["results"]}
        assert outcomes == {"started", "failed"}
        assert body["results"][0]["user"]["email"] == registered_user["email"]

        failed = staff_client.get("/api/v1/admin/payments/?outcome=failed")
        assert failed.json()["count"] == 1
        row = failed.json()["results"][0]
        assert row["failure_code"] == "generic_decline"
        assert row["items"][0]["title"] == "Curso de Pasta"

        search = staff_client.get("/api/v1/admin/payments/?search=user@recetario")
        assert search.json()["count"] == 2

        detail = staff_client.get(f"/api/v1/admin/payments/{row['id']}/")
        assert detail.status_code == 200
        assert detail.json()["data"]["order_id"] == order_id
        assert detail.json()["data"]["order_status"] == "failed"


def _checkout_order(published_course, registered_user, monkeypatch) -> str:
    client = _user_client(registered_user)
    client.post("/api/v1/me/cart/", {"course_id": published_course["id"]}, format="json")
    monkeypatch.setattr(
        "apps.commerce.services.checkout_service.create_stripe_checkout_session",
        lambda **kwargs: SimpleNamespace(
            id="cs_test_123", url="https://checkout.stripe.com/c/pay/cs_test_123"
        ),
    )
    checkout = client.post("/api/v1/checkout/create-session/", {"lang": "es"}, format="json")
    assert checkout.status_code == 200, checkout.json()
    return checkout.json()["data"]["order_id"]


def _post_webhook(monkeypatch, event: dict):
    monkeypatch.setattr(
        "apps.commerce.services.webhook_service.construct_stripe_event",
        lambda **kwargs: event,
    )
    response = APIClient().post(
        "/api/v1/webhooks/stripe/",
        data="{}",
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="t=1,v1=test",
    )
    assert response.status_code == 200, response.json()
    return response
