from django.db.models import Prefetch

from apps.catalog.models import CourseTranslation, Language, RecipeTranslation
from apps.commerce.models import Cart, Purchase


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
