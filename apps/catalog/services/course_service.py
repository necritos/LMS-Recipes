from decimal import Decimal

from django.db import transaction

from apps.catalog.constants import CourseFormat, PublishStatus
from apps.catalog.models import Course, CourseTranslation
from apps.catalog.services.category_service import _get_language_map
from apps.common.exceptions import BusinessError

_FORMAT_KEYS = ("format", "event_starts_at", "event_address", "maps_url")


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


def _ensure_in_person_has_no_content(*, course: Course) -> None:
    if course.modules.exists() or course.resources.exists():
        raise BusinessError(
            "IN_PERSON_HAS_CONTENT",
            "Un curso presencial no puede tener módulos ni recursos. "
            "Elimínalos antes de cambiar el formato.",
            http_status=422,
        )


def resolve_course_format_fields(*, course: Course | None = None, **incoming) -> dict:
    resolved_format = incoming.get("format", course.format if course else CourseFormat.ONLINE)
    starts = incoming.get("event_starts_at", course.event_starts_at if course else None)
    address = incoming.get("event_address", course.event_address if course else "")
    maps = incoming.get("maps_url", course.maps_url if course else "")

    if resolved_format == CourseFormat.IN_PERSON:
        address = (address or "").strip()
        maps = (maps or "").strip()
        if starts is None or not address or not maps:
            raise BusinessError(
                "IN_PERSON_EVENT_REQUIRED",
                "Un curso presencial necesita fecha/hora, dirección y enlace de Google Maps.",
                http_status=422,
            )
        if course is not None and course.format != CourseFormat.IN_PERSON:
            _ensure_in_person_has_no_content(course=course)
        return {
            "format": CourseFormat.IN_PERSON,
            "event_starts_at": starts,
            "event_address": address,
            "maps_url": maps,
        }

    return {
        "format": CourseFormat.ONLINE,
        "event_starts_at": None,
        "event_address": "",
        "maps_url": "",
    }


def _extract_format_kwargs(fields: dict) -> dict:
    return {key: fields.pop(key) for key in _FORMAT_KEYS if key in fields}


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
    format: str = CourseFormat.ONLINE,
    event_starts_at=None,
    event_address: str = "",
    maps_url: str = "",
) -> Course:
    if Course.objects.filter(slug=slug).exists():
        raise BusinessError(
            "SLUG_ALREADY_EXISTS",
            "Ya existe un curso con este slug.",
            http_status=409,
        )

    format_fields = resolve_course_format_fields(
        format=format,
        event_starts_at=event_starts_at,
        event_address=event_address,
        maps_url=maps_url,
    )
    course = Course.objects.create(
        slug=slug,
        price=price,
        access_days=access_days,
        category_id=category_id,
        status=status,
        sort_order=sort_order,
        **format_fields,
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
    format_kwargs = _extract_format_kwargs(fields)
    format_fields = resolve_course_format_fields(course=course, **format_kwargs)

    if (
        "slug" in fields
        and Course.objects.exclude(pk=course.pk).filter(slug=fields["slug"]).exists()
    ):
        raise BusinessError(
            "SLUG_ALREADY_EXISTS",
            "Ya existe un curso con este slug.",
            http_status=409,
        )

    for key, value in fields.items():
        setattr(course, key, value)
    for key, value in format_fields.items():
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
