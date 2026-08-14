import logging

from django.db import transaction
from django.utils import timezone

from apps.commerce.models import Order, Purchase, StripeEvent
from apps.commerce.services.cart_service import get_or_create_cart
from apps.commerce.services.grants import upsert_access_grant
from apps.commerce.services.stripe_client import construct_stripe_event
from apps.common.exceptions import BusinessError
from apps.notifications.services.mail import dispatch_transactional_email
from apps.site.selectors import get_site_settings

logger = logging.getLogger(__name__)


def _as_dict(obj) -> dict:
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return dict(obj)


def parse_stripe_event(*, payload: bytes, sig_header: str):
    settings = get_site_settings()
    secret = (settings.stripe_webhook_secret or "").strip()
    if not secret:
        raise BusinessError(
            "STRIPE_WEBHOOK_NOT_CONFIGURED",
            "Falta el webhook secret de Stripe en el admin.",
            http_status=503,
        )
    try:
        return construct_stripe_event(payload=payload, sig_header=sig_header, webhook_secret=secret)
    except Exception as exc:
        if type(exc).__name__ == "SignatureVerificationError":
            raise BusinessError(
                "STRIPE_SIGNATURE_INVALID",
                "La firma del webhook de Stripe no es válida.",
                http_status=400,
            ) from exc
        raise BusinessError(
            "STRIPE_PAYLOAD_INVALID",
            "El payload del webhook no es válido.",
            http_status=400,
        ) from exc


@transaction.atomic
def process_stripe_event(event) -> dict:
    event = _as_dict(event)
    event_id = event["id"]
    event_type = event["type"]
    _, created = StripeEvent.objects.get_or_create(
        event_id=event_id,
        defaults={"event_type": event_type},
    )
    if not created:
        return {"status": "duplicate", "event_id": event_id}

    payload = _as_dict(event.get("data") or {}).get("object") or {}
    payload = _as_dict(payload)
    if event_type == "checkout.session.completed":
        fulfill_checkout_session(payload)
    elif event_type in {"payment_intent.payment_failed", "checkout.session.expired"}:
        mark_order_failed(payload)

    return {"status": "processed", "event_id": event_id, "type": event_type}


def _payment_intent_id(obj: dict) -> str:
    raw = obj.get("payment_intent") or ""
    if obj.get("object") == "payment_intent":
        raw = obj.get("id") or raw
    if isinstance(raw, dict):
        return raw.get("id") or ""
    return str(raw) if raw else ""


def _order_from_stripe_object(obj: dict) -> Order | None:
    metadata = _as_dict(obj.get("metadata") or {})
    order_id = metadata.get("order_id")
    if order_id:
        order = Order.objects.filter(pk=order_id).first()
        if order:
            return order
    if obj.get("object") == "checkout.session" and obj.get("id"):
        return Order.objects.filter(stripe_session_id=obj["id"]).first()
    payment_intent = _payment_intent_id(obj)
    if payment_intent:
        return Order.objects.filter(stripe_payment_intent=payment_intent).first()
    return None


def fulfill_checkout_session(session: dict) -> None:
    session = _as_dict(session)
    order = _order_from_stripe_object(session)
    if order is None:
        logger.warning("Webhook checkout sin order: %s", session.get("id"))
        return
    if order.status == Order.Status.PAID:
        return

    order.status = Order.Status.PAID
    order.paid_at = timezone.now()
    order.stripe_payment_intent = _payment_intent_id(session)
    if session.get("id"):
        order.stripe_session_id = session["id"]
    order.save(
        update_fields=[
            "status",
            "paid_at",
            "stripe_payment_intent",
            "stripe_session_id",
            "updated_at",
        ]
    )

    for item in order.items.select_related("course", "recipe"):
        grant = upsert_access_grant(user=order.user, item=item)
        Purchase.objects.create(
            user=order.user,
            order=order,
            course=item.course,
            recipe=item.recipe,
            access_grant=grant,
        )

    get_or_create_cart(user=order.user).items.all().delete()
    _send_purchase_email(order)


def mark_order_failed(obj: dict) -> None:
    order = _order_from_stripe_object(_as_dict(obj))
    if order is None or order.status == Order.Status.PAID:
        return
    order.status = Order.Status.FAILED
    order.save(update_fields=["status", "updated_at"])


def _send_purchase_email(order: Order) -> None:
    from django.conf import settings as django_settings

    items = list(order.items.all())
    try:
        dispatch_transactional_email(
            to=order.customer_email or order.user.email,
            subject=f"Confirmación de compra — {django_settings.SITE_NAME}",
            template_name="notifications/emails/purchase_confirmation.html",
            context={
                "site_name": django_settings.SITE_NAME,
                "user_name": order.user.first_name or order.user.email,
                "order_id": str(order.id),
                "total": str(order.total),
                "currency": order.currency.upper(),
                "items": [{"title": item.title, "price": str(item.unit_price)} for item in items],
            },
            require_mail=False,
        )
    except Exception:
        logger.exception("No se pudo enviar email de compra para order %s", order.id)
