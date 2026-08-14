from decimal import Decimal

import stripe

from apps.common.exceptions import BusinessError
from apps.site.selectors import get_site_settings


def require_stripe_settings():
    settings = get_site_settings()
    if (
        not settings.stripe_enabled
        or not settings.stripe_secret_key.strip()
        or not settings.stripe_success_url.strip()
        or not settings.stripe_cancel_url.strip()
    ):
        raise BusinessError(
            "STRIPE_NOT_CONFIGURED",
            "Stripe no está configurado. Actívalo en el admin.",
            http_status=503,
        )
    return settings


def amount_to_cents(amount: Decimal) -> int:
    return int((amount * 100).quantize(Decimal("1")))


def with_checkout_session_id(url: str) -> str:
    if "{CHECKOUT_SESSION_ID}" in url:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}session_id={{CHECKOUT_SESSION_ID}}"


def create_stripe_checkout_session(*, secret_key: str, params: dict):
    stripe.api_key = secret_key
    return stripe.checkout.Session.create(**params)


def construct_stripe_event(*, payload: bytes, sig_header: str, webhook_secret: str):
    return stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
