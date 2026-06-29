from decimal import Decimal

from django.db import transaction

from apps.catalog.constants import PublishStatus, RecipeAccessType
from apps.catalog.models import Recipe, RecipeTranslation
from apps.catalog.services.category_service import _get_language_map
from apps.common.exceptions import BusinessError


def _validate_recipe_access(*, access_type: str, access_days: int | None) -> None:
    if access_type == RecipeAccessType.TIMED and not access_days:
        raise BusinessError(
            "ACCESS_DAYS_REQUIRED",
            "Las recetas con acceso limitado requieren access_days.",
            http_status=422,
        )
    if access_type == RecipeAccessType.LIFETIME:
        return


def _upsert_recipe_translations(*, recipe: Recipe, translations: list[dict]) -> None:
    if not translations:
        raise BusinessError(
            "TRANSLATIONS_REQUIRED",
            "Debes incluir al menos una traducción.",
            http_status=422,
        )
    recipe.translations.all().delete()
    lang_map = _get_language_map([item["language_code"] for item in translations])
    for item in translations:
        language = lang_map[item["language_code"].strip().lower()]
        RecipeTranslation.objects.create(
            recipe=recipe,
            language=language,
            title=item["title"].strip(),
            description=item.get("description", ""),
            meta_title=item.get("meta_title", ""),
            meta_description=item.get("meta_description", ""),
        )


@transaction.atomic
def create_recipe(
    *,
    slug: str,
    price: Decimal,
    translations: list[dict],
    access_type: str = RecipeAccessType.LIFETIME,
    access_days: int | None = None,
    category_id=None,
    status: str = PublishStatus.DRAFT,
    sort_order: int = 0,
    cover_image=None,
) -> Recipe:
    _validate_recipe_access(access_type=access_type, access_days=access_days)
    if Recipe.objects.filter(slug=slug).exists():
        raise BusinessError(
            "SLUG_ALREADY_EXISTS",
            "Ya existe una receta con este slug.",
            http_status=409,
        )

    recipe = Recipe.objects.create(
        slug=slug,
        price=price,
        access_type=access_type,
        access_days=access_days if access_type == RecipeAccessType.TIMED else None,
        category_id=category_id,
        status=status,
        sort_order=sort_order,
    )
    if cover_image is not None:
        recipe.cover_image = cover_image
        recipe.save(update_fields=["cover_image", "updated_at"])
    _upsert_recipe_translations(recipe=recipe, translations=translations)
    return recipe


@transaction.atomic
def update_recipe(*, recipe: Recipe, **fields) -> Recipe:
    translations = fields.pop("translations", None)
    cover_image = fields.pop("cover_image", None)

    access_type = fields.get("access_type", recipe.access_type)
    access_days = fields.get("access_days", recipe.access_days)
    _validate_recipe_access(access_type=access_type, access_days=access_days)

    if access_type == RecipeAccessType.LIFETIME:
        fields["access_days"] = None
    elif "access_days" not in fields:
        fields["access_days"] = access_days

    if "slug" in fields and Recipe.objects.exclude(pk=recipe.pk).filter(
        slug=fields["slug"]
    ).exists():
        raise BusinessError(
            "SLUG_ALREADY_EXISTS",
            "Ya existe una receta con este slug.",
            http_status=409,
        )

    for key, value in fields.items():
        setattr(recipe, key, value)
    if cover_image is not None:
        recipe.cover_image = cover_image
    recipe.save()

    if translations is not None:
        _upsert_recipe_translations(recipe=recipe, translations=translations)
    return recipe


@transaction.atomic
def delete_recipe(*, recipe: Recipe) -> None:
    recipe.delete()
