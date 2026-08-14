from django.db import transaction
from django.utils import timezone

from apps.content.models import Lesson, LessonProgress
from apps.content.services.access_service import require_active_access


@transaction.atomic
def complete_lesson(*, user, lesson: Lesson) -> LessonProgress:
    require_active_access(user=user, course=lesson.module.course)
    now = timezone.now()
    progress, created = LessonProgress.objects.get_or_create(
        user=user,
        lesson=lesson,
        defaults={"completed": True, "completed_at": now, "last_viewed_at": now},
    )
    if created:
        return progress
    progress.last_viewed_at = now
    if not progress.completed:
        progress.completed = True
        progress.completed_at = now
    progress.save(update_fields=["completed", "completed_at", "last_viewed_at", "updated_at"])
    return progress


@transaction.atomic
def record_lesson_view(*, user, lesson: Lesson) -> LessonProgress:
    require_active_access(user=user, course=lesson.module.course)
    now = timezone.now()
    progress, created = LessonProgress.objects.get_or_create(
        user=user,
        lesson=lesson,
        defaults={"last_viewed_at": now},
    )
    if created:
        return progress
    progress.last_viewed_at = now
    progress.save(update_fields=["last_viewed_at", "updated_at"])
    return progress
