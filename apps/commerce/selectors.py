from django.db.models import Prefetch, Q, QuerySet

from apps.catalog.models import Course, CourseTranslation, Language, RecipeTranslation
from apps.commerce.models import Cart, PaymentAttempt, Purchase


def cart_for_user(*, user, language: Language | None = None) -> Cart:
    cart, _ = Cart.objects.get_or_create(user=user)
    qs = Cart.objects.filter(pk=cart.pk).prefetch_related(
        "items__course",
        "items__recipe",
    )
    if language is not None:
        qs = qs.prefetch_related(
            Prefetch(
                "items__course__translations",
                queryset=CourseTranslation.objects.filter(language=language),
                to_attr="active_translations",
            ),
            Prefetch(
                "items__recipe__translations",
                queryset=RecipeTranslation.objects.filter(language=language),
                to_attr="active_translations",
            ),
        )
    return qs.get()


def purchases_for_user(*, user, language: Language):
    return (
        Purchase.objects.filter(user=user)
        .select_related("order", "course", "recipe", "access_grant")
        .prefetch_related(
            "order__items",
            Prefetch(
                "course__translations",
                queryset=CourseTranslation.objects.filter(language=language),
                to_attr="active_translations",
            ),
            Prefetch(
                "recipe__translations",
                queryset=RecipeTranslation.objects.filter(language=language),
                to_attr="active_translations",
            ),
        )
        .order_by("-created_at")
    )


def purchases_for_course(*, course: Course):
    return (
        Purchase.objects.filter(course=course)
        .select_related("user", "order", "access_grant")
        .order_by("-created_at")
    )


def payment_attempts_for_admin(
    *, outcome: str | None = None, search: str = ""
) -> QuerySet[PaymentAttempt]:
    qs = PaymentAttempt.objects.select_related("user", "order").prefetch_related("order__items")
    if outcome in PaymentAttempt.Outcome.values:
        qs = qs.filter(outcome=outcome)
    if search:
        qs = qs.filter(
            Q(customer_email__icontains=search)
            | Q(user__email__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(stripe_session_id__icontains=search)
            | Q(stripe_payment_intent__icontains=search)
        )
    return qs.order_by("-created_at")
