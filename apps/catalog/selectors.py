from django.db.models import Prefetch, Q, QuerySet

from apps.catalog.constants import PublishStatus
from apps.catalog.models import (
    Category,
    CategoryTranslation,
    Course,
    CourseTranslation,
    Language,
    Recipe,
    RecipeTranslation,
)
from apps.common.exceptions import BusinessError


def resolve_language_code(lang: str | None) -> str:
    code = (lang or "es").strip().lower()
    if not code:
        return "es"
    return code


def get_active_language(*, code: str) -> Language:
    language = Language.objects.filter(code=code, is_active=True).first()
    if language is None:
        raise BusinessError(
            "LANGUAGE_NOT_FOUND",
            f"El idioma '{code}' no está disponible.",
            http_status=404,
        )
    return language


def list_active_languages() -> QuerySet[Language]:
    return Language.objects.filter(is_active=True).order_by("code")


def categories_for_public(*, language: Language) -> QuerySet[Category]:
    return (
        Category.objects.filter(is_active=True, translations__language=language)
        .distinct()
        .prefetch_related(
            Prefetch(
                "translations",
                queryset=CategoryTranslation.objects.filter(language=language),
                to_attr="active_translations",
            )
        )
        .order_by("sort_order", "slug")
    )


def courses_for_public(
    *,
    language: Language,
    category_slug: str | None = None,
    search: str | None = None,
) -> QuerySet[Course]:
    qs = Course.objects.filter(
        status=PublishStatus.PUBLISHED,
        translations__language=language,
    ).distinct()
    if category_slug:
        qs = qs.filter(category__slug=category_slug, category__is_active=True)
    if search:
        qs = qs.filter(
            Q(translations__title__icontains=search)
            | Q(translations__description__icontains=search)
        )
    return qs.prefetch_related(
        "category",
        Prefetch(
            "translations",
            queryset=CourseTranslation.objects.filter(language=language),
            to_attr="active_translations",
        ),
    ).order_by("sort_order", "slug")


def get_published_course(*, slug: str, language: Language) -> Course:
    course = (
        Course.objects.filter(
            slug=slug,
            status=PublishStatus.PUBLISHED,
            translations__language=language,
        )
        .prefetch_related(
            "category",
            Prefetch(
                "translations",
                queryset=CourseTranslation.objects.filter(language=language),
                to_attr="active_translations",
            ),
        )
        .first()
    )
    if course is None:
        raise BusinessError(
            "COURSE_NOT_FOUND",
            "Curso no encontrado.",
            http_status=404,
        )
    return course


def recipes_for_public(
    *,
    language: Language,
    category_slug: str | None = None,
    search: str | None = None,
) -> QuerySet[Recipe]:
    qs = Recipe.objects.filter(
        status=PublishStatus.PUBLISHED,
        translations__language=language,
    ).distinct()
    if category_slug:
        qs = qs.filter(category__slug=category_slug, category__is_active=True)
    if search:
        qs = qs.filter(
            Q(translations__title__icontains=search)
            | Q(translations__description__icontains=search)
        )
    return qs.prefetch_related(
        "category",
        Prefetch(
            "translations",
            queryset=RecipeTranslation.objects.filter(language=language),
            to_attr="active_translations",
        ),
    ).order_by("sort_order", "slug")


def get_published_recipe(*, slug: str, language: Language) -> Recipe:
    recipe = (
        Recipe.objects.filter(
            slug=slug,
            status=PublishStatus.PUBLISHED,
            translations__language=language,
        )
        .prefetch_related(
            "category",
            Prefetch(
                "translations",
                queryset=RecipeTranslation.objects.filter(language=language),
                to_attr="active_translations",
            ),
        )
        .first()
    )
    if recipe is None:
        raise BusinessError(
            "RECIPE_NOT_FOUND",
            "Receta no encontrada.",
            http_status=404,
        )
    return recipe
