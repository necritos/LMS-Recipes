from django.db import transaction

from apps.catalog.api.serializers_helpers import get_active_translation
from apps.commerce.models import Order, OrderItem
from apps.commerce.services.cart_service import cart_total, get_or_create_cart
from apps.commerce.services.grants import snapshot_access
from apps.commerce.services.stripe_client import (
    amount_to_cents,
    create_stripe_checkout_session,
    require_stripe_settings,
    with_checkout_session_id,
)
from apps.common.exceptions import BusinessError


def _item_title(item, lang: str) -> str:
    product = item.course or item.recipe
    translation = product.translations.filter(language__code=lang).first()
    if translation:
        return translation.title
    return get_active_translation(product, "title") or product.slug


@transaction.atomic
def create_checkout_session(*, user, lang: str = "es") -> dict:
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

    session = create_stripe_checkout_session(
        secret_key=settings.stripe_secret_key,
        params={
            "mode": "payment",
            "customer_email": user.email,
            "success_url": with_checkout_session_id(settings.stripe_success_url),
            "cancel_url": settings.stripe_cancel_url,
            "line_items": line_items,
            "metadata": {"user_id": str(user.id), "order_id": str(order.id)},
            "payment_intent_data": {"metadata": {"order_id": str(order.id)}},
            "locale": lang if lang in {"es", "en", "sk", "de", "fr", "it", "pt"} else "auto",
        },
    )
    order.stripe_session_id = session.id
    order.save(update_fields=["stripe_session_id", "updated_at"])
    return {
        "checkout_url": session.url,
        "session_id": session.id,
        "order_id": str(order.id),
        "total": str(total),
        "currency": settings.stripe_currency,
    }
