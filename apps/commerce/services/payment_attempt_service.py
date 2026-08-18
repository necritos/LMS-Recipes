from apps.commerce.models import Order, PaymentAttempt


def record_payment_attempt(
    *,
    order: Order,
    outcome: str,
    stripe_event_id: str = "",
    stripe_event_type: str = "",
    stripe_payment_intent: str = "",
    failure_code: str = "",
    failure_message: str = "",
) -> PaymentAttempt:
    event_id = (stripe_event_id or "").strip() or None
    if event_id:
        existing = PaymentAttempt.objects.filter(stripe_event_id=event_id).first()
        if existing:
            return existing
    return PaymentAttempt.objects.create(
        order=order,
        user=order.user,
        outcome=outcome,
        amount=order.total,
        currency=order.currency,
        customer_email=order.customer_email or order.user.email,
        stripe_session_id=order.stripe_session_id or "",
        stripe_payment_intent=stripe_payment_intent or order.stripe_payment_intent or "",
        stripe_event_id=event_id,
        stripe_event_type=stripe_event_type,
        failure_code=(failure_code or "")[:80],
        failure_message=failure_message or "",
    )
