from django.db.models import Prefetch, QuerySet

from apps.catalog.models import Course, Language, Recipe
from apps.common.exceptions import BusinessError
from apps.content.models import Lesson, LessonTranslation, Module, ModuleTranslation


def get_course_or_404(*, course_id) -> Course:
    course = Course.objects.filter(pk=course_id).first()
    if course is None:
        raise BusinessError("COURSE_NOT_FOUND", "Curso no encontrado.", http_status=404)
    return course


def get_recipe_or_404(*, recipe_id) -> Recipe:
    recipe = Recipe.objects.filter(pk=recipe_id).first()
    if recipe is None:
        raise BusinessError("RECIPE_NOT_FOUND", "Receta no encontrada.", http_status=404)
    return recipe


def get_module_for_course(*, course: Course, module_id) -> Module:
    module = Module.objects.filter(pk=module_id, course=course).first()
    if module is None:
        raise BusinessError("MODULE_NOT_FOUND", "Módulo no encontrado.", http_status=404)
    return module


def _prefetch_lang(qs, translation_model, language: Language):
    return (
        qs.filter(translations__language=language)
        .distinct()
        .prefetch_related(
            Prefetch(
                "translations",
                queryset=translation_model.objects.filter(language=language),
                to_attr="active_translations",
            )
        )
    )


def public_modules_for_course(*, course: Course, language: Language) -> QuerySet[Module]:
    modules = _prefetch_lang(
        Module.objects.filter(course=course, is_active=True),
        ModuleTranslation,
        language,
    )
    lessons_qs = _prefetch_lang(
        Lesson.objects.filter(is_active=True),
        LessonTranslation,
        language,
    )
    return modules.prefetch_related(Prefetch("lessons", queryset=lessons_qs)).order_by(
        "sort_order", "created_at"
    )


def player_modules_for_course(*, course: Course, language: Language) -> QuerySet[Module]:
    return public_modules_for_course(course=course, language=language)


def admin_modules_for_course(*, course: Course) -> QuerySet[Module]:
    return (
        Module.objects.filter(course=course)
        .prefetch_related("translations__language", "lessons__translations__language")
        .order_by("sort_order", "created_at")
    )


def admin_lessons_for_module(*, module: Module) -> QuerySet[Lesson]:
    return module.lessons.prefetch_related("translations__language").order_by(
        "sort_order", "created_at"
    )
