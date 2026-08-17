from django.db import transaction

from apps.catalog.services.category_service import _get_language_map
from apps.common.exceptions import BusinessError
from apps.content.models import Lesson, LessonTranslation, Module, ModuleTranslation


def _require_translations(translations: list[dict] | None) -> list[dict]:
    if not translations:
        raise BusinessError(
            "TRANSLATIONS_REQUIRED",
            "Debes incluir al menos una traducción.",
            http_status=422,
        )
    return translations


def upsert_module_translations(*, module: Module, translations: list[dict]) -> None:
    translations = _require_translations(translations)
    module.translations.all().delete()
    lang_map = _get_language_map([item["language_code"] for item in translations])
    for item in translations:
        language = lang_map[item["language_code"].strip().lower()]
        title = (item.get("title") or "").strip()
        if not title:
            raise BusinessError(
                "TRANSLATION_TITLE_REQUIRED",
                "Cada traducción del módulo necesita title.",
                http_status=422,
            )
        ModuleTranslation.objects.create(
            module=module,
            language=language,
            title=title,
            description=item.get("description", "") or "",
        )


def upsert_lesson_translations(*, lesson: Lesson, translations: list[dict]) -> None:
    translations = _require_translations(translations)
    lesson.translations.all().delete()
    lang_map = _get_language_map([item["language_code"] for item in translations])
    for item in translations:
        language = lang_map[item["language_code"].strip().lower()]
        title = (item.get("title") or "").strip()
        if not title:
            raise BusinessError(
                "TRANSLATION_TITLE_REQUIRED",
                "Cada traducción de la lección necesita title.",
                http_status=422,
            )
        LessonTranslation.objects.create(
            lesson=lesson,
            language=language,
            title=title,
            description=item.get("description", "") or "",
            content_html=item.get("content_html", "") or "",
        )


def assert_course_allows_curriculum(*, course) -> None:
    from apps.catalog.constants import CourseFormat

    if course.format == CourseFormat.IN_PERSON:
        raise BusinessError(
            "IN_PERSON_NO_CURRICULUM",
            "Los cursos presenciales no tienen módulos ni lecciones.",
            http_status=422,
        )


@transaction.atomic
def create_module(*, course, translations: list[dict] | None = None, **fields) -> Module:
    assert_course_allows_curriculum(course=course)
    module = Module.objects.create(course=course, **fields)
    upsert_module_translations(module=module, translations=translations)
    return module


@transaction.atomic
def update_module(*, module: Module, **fields) -> Module:
    translations = fields.pop("translations", None)
    for key, value in fields.items():
        setattr(module, key, value)
    module.save()
    if translations is not None:
        upsert_module_translations(module=module, translations=translations)
    return module


@transaction.atomic
def delete_module(*, module: Module) -> None:
    module.delete()


@transaction.atomic
def create_lesson(*, module: Module, translations: list[dict] | None = None, **fields) -> Lesson:
    lesson = Lesson.objects.create(module=module, **fields)
    upsert_lesson_translations(lesson=lesson, translations=translations)
    return lesson


@transaction.atomic
def update_lesson(*, lesson: Lesson, **fields) -> Lesson:
    translations = fields.pop("translations", None)
    for key, value in fields.items():
        setattr(lesson, key, value)
    lesson.save()
    if translations is not None:
        upsert_lesson_translations(lesson=lesson, translations=translations)
    return lesson


@transaction.atomic
def delete_lesson(*, lesson: Lesson) -> None:
    lesson.delete()
