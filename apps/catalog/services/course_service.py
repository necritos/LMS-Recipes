from decimal import Decimal

from django.db import transaction

from apps.catalog.constants import PublishStatus
from apps.catalog.models import Course, CourseTranslation
from apps.catalog.services.category_service import _get_language_map
from apps.common.exceptions import BusinessError


def _upsert_course_translations(*, course: Course, translations: list[dict]) -> None:
    if not translations:
        raise BusinessError(
            "TRANSLATIONS_REQUIRED",
            "Debes incluir al menos una traducción.",
            http_status=422,
        )
    course.translations.all().delete()
    lang_map = _get_language_map([item["language_code"] for item in translations])
    for item in translations:
        language = lang_map[item["language_code"].strip().lower()]
        CourseTranslation.objects.create(
            course=course,
            language=language,
            title=item["title"].strip(),
            description=item.get("description", ""),
            meta_title=item.get("meta_title", ""),
            meta_description=item.get("meta_description", ""),
        )


@transaction.atomic
def create_course(
    *,
    slug: str,
    price: Decimal,
    translations: list[dict],
    access_days: int = 365,
    category_id=None,
    status: str = PublishStatus.DRAFT,
    sort_order: int = 0,
    cover_image=None,
) -> Course:
    if Course.objects.filter(slug=slug).exists():
        raise BusinessError(
            "SLUG_ALREADY_EXISTS",
            "Ya existe un curso con este slug.",
            http_status=409,
        )

    course = Course.objects.create(
        slug=slug,
        price=price,
        access_days=access_days,
        category_id=category_id,
        status=status,
        sort_order=sort_order,
    )
    if cover_image is not None:
        course.cover_image = cover_image
        course.save(update_fields=["cover_image", "updated_at"])
    _upsert_course_translations(course=course, translations=translations)
    return course


@transaction.atomic
def update_course(*, course: Course, **fields) -> Course:
    translations = fields.pop("translations", None)
    cover_image = fields.pop("cover_image", None)

    if "slug" in fields and Course.objects.exclude(pk=course.pk).filter(
        slug=fields["slug"]
    ).exists():
        raise BusinessError(
            "SLUG_ALREADY_EXISTS",
            "Ya existe un curso con este slug.",
            http_status=409,
        )

    for key, value in fields.items():
        setattr(course, key, value)
    if cover_image is not None:
        course.cover_image = cover_image
    course.save()

    if translations is not None:
        _upsert_course_translations(course=course, translations=translations)
    return course


@transaction.atomic
def delete_course(*, course: Course) -> None:
    course.delete()
