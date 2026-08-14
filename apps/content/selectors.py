from django.db.models import Prefetch, Q, QuerySet
from django.utils import timezone

from apps.catalog.models import Course, CourseTranslation, Language, Recipe, RecipeTranslation
from apps.common.exceptions import BusinessError
from apps.content.models import (
    AccessGrant,
    Lesson,
    LessonProgress,
    LessonTranslation,
    Module,
    ModuleTranslation,
)


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


def get_lesson_or_404(*, lesson_id) -> Lesson:
    lesson = (
        Lesson.objects.select_related("module__course")
        .filter(pk=lesson_id, is_active=True, module__is_active=True)
        .first()
    )
    if lesson is None:
        raise BusinessError("LESSON_NOT_FOUND", "Lección no encontrada.", http_status=404)
    return lesson


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


def _active_grants_qs(*, user):
    now = timezone.now()
    return AccessGrant.objects.filter(user=user, is_revoked=False).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=now)
    )


def active_course_grants(*, user, language: Language) -> QuerySet[AccessGrant]:
    return (
        _active_grants_qs(user=user)
        .filter(course__isnull=False)
        .select_related("course")
        .prefetch_related(
            Prefetch(
                "course__translations",
                queryset=CourseTranslation.objects.filter(language=language),
                to_attr="active_translations",
            )
        )
        .order_by("-created_at")
    )


def active_recipe_grants(*, user, language: Language) -> QuerySet[AccessGrant]:
    return (
        _active_grants_qs(user=user)
        .filter(recipe__isnull=False)
        .select_related("recipe")
        .prefetch_related(
            Prefetch(
                "recipe__translations",
                queryset=RecipeTranslation.objects.filter(language=language),
                to_attr="active_translations",
            )
        )
        .order_by("-created_at")
    )


def active_lessons_for_course(
    *, course: Course, language: Language | None = None
) -> QuerySet[Lesson]:
    qs = Lesson.objects.filter(
        module__course=course,
        module__is_active=True,
        is_active=True,
    ).select_related("module")
    if language is not None:
        qs = qs.prefetch_related(
            Prefetch(
                "translations",
                queryset=LessonTranslation.objects.filter(language=language),
                to_attr="active_translations",
            )
        )
    return qs.order_by("module__sort_order", "module__created_at", "sort_order", "created_at")


def continue_lesson_for_course(
    *, user, course: Course, language: Language | None = None
) -> Lesson | None:
    lessons = list(active_lessons_for_course(course=course, language=language))
    if not lessons:
        return None
    latest = (
        LessonProgress.objects.filter(
            user=user,
            lesson__in=lessons,
            last_viewed_at__isnull=False,
        )
        .order_by("-last_viewed_at")
        .select_related("lesson__module")
        .first()
    )
    if latest:
        return next((lesson for lesson in lessons if lesson.pk == latest.lesson_id), latest.lesson)
    return lessons[0]


def progress_rows_for_course(*, user, course: Course) -> dict:
    return {
        row.lesson_id: row
        for row in LessonProgress.objects.filter(user=user, lesson__module__course=course)
    }
