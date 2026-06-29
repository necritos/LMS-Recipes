from django.db import transaction

from apps.catalog.models import Category, CategoryTranslation, Language
from apps.common.exceptions import BusinessError


def _get_language_map(codes: list[str]) -> dict[str, Language]:
    normalized = [_c.strip().lower() for _c in codes if _c.strip()]
    languages = Language.objects.filter(code__in=normalized)
    lang_map = {lang.code: lang for lang in languages}
    missing = set(normalized) - set(lang_map)
    if missing:
        raise BusinessError(
            "LANGUAGE_NOT_FOUND",
            f"Idiomas no encontrados: {', '.join(sorted(missing))}",
            http_status=422,
        )
    return lang_map


@transaction.atomic
def create_category(
    *,
    slug: str,
    translations: list[dict],
    sort_order: int = 0,
    is_active: bool = True,
) -> Category:
    if Category.objects.filter(slug=slug).exists():
        raise BusinessError(
            "SLUG_ALREADY_EXISTS",
            "Ya existe una categoría con este slug.",
            http_status=409,
        )
    if not translations:
        raise BusinessError(
            "TRANSLATIONS_REQUIRED",
            "Debes incluir al menos una traducción.",
            http_status=422,
        )

    category = Category.objects.create(slug=slug, sort_order=sort_order, is_active=is_active)
    lang_map = _get_language_map([item["language_code"] for item in translations])
    for item in translations:
        language = lang_map[item["language_code"].strip().lower()]
        CategoryTranslation.objects.create(
            category=category,
            language=language,
            name=item["name"].strip(),
            description=item.get("description", ""),
        )
    return category


@transaction.atomic
def update_category(*, category: Category, **fields) -> Category:
    translations = fields.pop("translations", None)
    if "slug" in fields and Category.objects.exclude(pk=category.pk).filter(
        slug=fields["slug"]
    ).exists():
        raise BusinessError(
            "SLUG_ALREADY_EXISTS",
            "Ya existe una categoría con este slug.",
            http_status=409,
        )

    for key, value in fields.items():
        setattr(category, key, value)
    category.save()

    if translations is not None:
        if not translations:
            raise BusinessError(
                "TRANSLATIONS_REQUIRED",
                "Debes incluir al menos una traducción.",
                http_status=422,
            )
        category.translations.all().delete()
        lang_map = _get_language_map([item["language_code"] for item in translations])
        for item in translations:
            language = lang_map[item["language_code"].strip().lower()]
            CategoryTranslation.objects.create(
                category=category,
                language=language,
                name=item["name"].strip(),
                description=item.get("description", ""),
            )
    return category
