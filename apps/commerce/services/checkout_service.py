import os
import re
from urllib.parse import urlparse

from django.conf import settings as django_settings
from django.db import transaction

from apps.catalog.api.serializers_helpers import get_active_translation
from apps.commerce.models import Order, OrderItem, PaymentAttempt
from apps.commerce.services.cart_service import cart_total, get_or_create_cart
from apps.commerce.services.grants import snapshot_access
from apps.commerce.services.payment_attempt_service import record_payment_attempt
from apps.commerce.services.stripe_client import (
    amount_to_cents,
    create_stripe_checkout_session,
    require_stripe_settings,
    with_checkout_session_id,
)
from apps.common.exceptions import BusinessError
from config.settings.cors_defaults import PRODUCTION_CORS_ORIGIN_REGEXES

_LOCALHOST_ORIGIN = re.compile(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$", re.I)


def _item_title(item, lang: str) -> str:
    product = item.course or item.recipe
    translation = product.translations.filter(language__code=lang).first()
    if translation:
        return translation.title
    return get_active_translation(product, "title") or product.slug


def _origin(url: str) -> str:
    parsed = urlparse((url or "").strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}".lower()


def _allowed_checkout_origins(*, settings) -> set[str]:
    origins: set[str] = set()
    for raw in getattr(django_settings, "CORS_ALLOWED_ORIGINS", []) or []:
        origin = _origin(raw)
        if origin:
            origins.add(origin)
    for raw in (settings.stripe_success_url, settings.stripe_cancel_url):
        origin = _origin(raw)
        if origin:
            origins.add(origin)
    return origins


def assert_checkout_redirect_allowed(*, url: str, settings) -> None:
    origin = _origin(url)
    if not origin:
        raise BusinessError(
            "CHECKOUT_REDIRECT_NOT_ALLOWED",
            "La URL de redirección de Stripe no es válida.",
            http_status=422,
        )
    if origin in _allowed_checkout_origins(settings=settings):
        return
    if any(re.fullmatch(pattern, origin) for pattern in PRODUCTION_CORS_ORIGIN_REGEXES):
        return
    allow_localhost = django_settings.DEBUG or os.environ.get(
        "CORS_ALLOW_LOCALHOST", ""
    ).lower() in {
        "true",
        "1",
        "yes",
    }
    if allow_localhost and _LOCALHOST_ORIGIN.fullmatch(origin):
        return
    raise BusinessError(
        "CHECKOUT_REDIRECT_NOT_ALLOWED",
        "La URL de redirección no pertenece a un dominio permitido.",
        http_status=422,
    )


def resolve_checkout_redirects(
    *,
    settings,
    stripe_success_url: str | None = None,
    stripe_cancel_url: str | None = None,
) -> tuple[str, str]:
    success = (stripe_success_url or "").strip() or settings.stripe_success_url
    cancel = (stripe_cancel_url or "").strip() or settings.stripe_cancel_url
    assert_checkout_redirect_allowed(url=success, settings=settings)
    assert_checkout_redirect_allowed(url=cancel, settings=settings)
    return with_checkout_session_id(success), cancel


@transaction.atomic
def create_checkout_session(
    *,
    user,
    lang: str = "es",
    stripe_success_url: str | None = None,
    stripe_cancel_url: str | None = None,
) -> dict:
    settings = require_stripe_settings()
    cart = get_or_create_cart(user=user)
    items = list(
        cart.items.select_related("course", "recipe").prefetch_related(
            "course__translations",
            "recipe__translations",
        )
    )
    if not items:
        raise BusinessError("CART_EMPTY", "El carrito está vacío.", http_status=422)

    total = cart_total(cart)
    if total <= 0:
        raise BusinessError(
            "CART_TOTAL_INVALID",
            "El total del carrito debe ser mayor que cero.",
            http_status=422,
        )

    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
        currency=settings.stripe_currency,
        total=total,
        customer_email=user.email,
    )
    line_items = []
    for item in items:
        product = item.course or item.recipe
        title = _item_title(item, lang)
        access_days, is_lifetime = snapshot_access(course=item.course, recipe=item.recipe)
        OrderItem.objects.create(
            order=order,
            course=item.course,
            recipe=item.recipe,
            title=title,
            unit_price=product.price,
            access_days=access_days,
            is_lifetime=is_lifetime,
        )
        line_items.append(
            {
                "quantity": 1,
                "price_data": {
                    "currency": settings.stripe_currency,
                    "unit_amount": amount_to_cents(product.price),
                    "product_data": {
                        "name": title,
                        "metadata": {
                            "product_type": "course" if item.course_id else "recipe",
                            "product_id": str(product.id),
                        },
                    },
                },
            }
        )

    success_url, cancel_url = resolve_checkout_redirects(
        settings=settings,
        stripe_success_url=stripe_success_url,
        stripe_cancel_url=stripe_cancel_url,
    )
    session = create_stripe_checkout_session(
        secret_key=settings.stripe_secret_key,
        params={
            "mode": "payment",
            "customer_email": user.email,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": line_items,
            "metadata": {"user_id": str(user.id), "order_id": str(order.id)},
            "payment_intent_data": {"metadata": {"order_id": str(order.id)}},
            "locale": lang if lang in {"es", "en", "sk", "de", "fr", "it", "pt"} else "auto",
        },
    )
    order.stripe_session_id = session.id
    order.save(update_fields=["stripe_session_id", "updated_at"])
    record_payment_attempt(
        order=order,
        outcome=PaymentAttempt.Outcome.STARTED,
        stripe_event_type="checkout.session.created",
    )
    return {
        "checkout_url": session.url,
        "session_id": session.id,
        "order_id": str(order.id),
        "total": str(total),
        "currency": settings.stripe_currency,
    }
