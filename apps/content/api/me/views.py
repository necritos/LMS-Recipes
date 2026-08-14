from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.api.serializers_helpers import get_active_translation
from apps.catalog.selectors import get_active_language, resolve_language_code
from apps.common.permissions import HasActiveAccess, IsAuthenticatedUser
from apps.content.api.me.serializers import (
    MeCourseAccessSerializer,
    MeLessonProgressWriteSerializer,
    MeModuleSerializer,
    MeRecipeAccessSerializer,
    continue_lesson_payload,
)
from apps.content.selectors import (
    active_course_grants,
    active_lessons_for_course,
    active_recipe_grants,
    get_course_or_404,
    get_lesson_or_404,
    get_recipe_or_404,
    player_modules_for_course,
    progress_rows_for_course,
)
from apps.content.services.progress_service import complete_lesson, record_lesson_view
from apps.content.services.video_service import issue_signed_video


class MeCourseLessonsView(APIView):
    permission_classes = [HasActiveAccess]

    def get_access_target(self):
        return {"course": get_course_or_404(course_id=self.kwargs["course_id"])}

    @extend_schema(
        tags=["Me"],
        parameters=[OpenApiParameter("lang", str, description="Código de idioma (default: es)")],
    )
    def get(self, request, course_id):
        course = get_course_or_404(course_id=course_id)
        language = get_active_language(code=resolve_language_code(request.query_params.get("lang")))
        modules = list(player_modules_for_course(course=course, language=language))
        signed_videos = {}
        for module in modules:
            for lesson in module.lessons.all():
                if not lesson.bunny_video_id:
                    continue
                signed_videos[str(lesson.pk)] = issue_signed_video(
                    user=request.user,
                    video_id=lesson.bunny_video_id,
                    lesson=lesson,
                )
        serializer = MeModuleSerializer(
            modules, many=True, context={"request": request, "signed_videos": signed_videos}
        )
        return Response(
            {"data": {"course_id": str(course.id), "modules": serializer.data}, "meta": {}}
        )


class MeRecipeVideoView(APIView):
    permission_classes = [HasActiveAccess]

    def get_access_target(self):
        return {"recipe": get_recipe_or_404(recipe_id=self.kwargs["recipe_id"])}

    @extend_schema(tags=["Me"])
    def get(self, request, recipe_id):
        recipe = get_recipe_or_404(recipe_id=recipe_id)
        video = issue_signed_video(
            user=request.user,
            video_id=recipe.bunny_video_id,
            recipe=recipe,
        )
        return Response({"data": {"recipe_id": str(recipe.id), "video": video}, "meta": {}})


def _lang(request):
    return get_active_language(code=resolve_language_code(request.query_params.get("lang")))


class MeCourseListView(ListAPIView):
    permission_classes = [IsAuthenticatedUser]
    serializer_class = MeCourseAccessSerializer

    @extend_schema(
        tags=["Me"],
        parameters=[OpenApiParameter("lang", str, description="Idioma de títulos (default: es)")],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return active_course_grants(user=self.request.user, language=_lang(self.request))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["language"] = _lang(self.request)
        return context


class MeRecipeListView(ListAPIView):
    permission_classes = [IsAuthenticatedUser]
    serializer_class = MeRecipeAccessSerializer

    @extend_schema(
        tags=["Me"],
        parameters=[OpenApiParameter("lang", str, description="Idioma de títulos (default: es)")],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return active_recipe_grants(user=self.request.user, language=_lang(self.request))


class MeLessonCompleteView(APIView):
    permission_classes = [HasActiveAccess]

    def get_access_target(self):
        lesson = get_lesson_or_404(lesson_id=self.kwargs["lesson_id"])
        return {"course": lesson.module.course}

    @extend_schema(tags=["Me"], request=None, responses=MeLessonProgressWriteSerializer)
    def post(self, request, lesson_id):
        lesson = get_lesson_or_404(lesson_id=lesson_id)
        progress = complete_lesson(user=request.user, lesson=lesson)
        return Response({"data": MeLessonProgressWriteSerializer(progress).data, "meta": {}})


class MeLessonViewView(APIView):
    permission_classes = [HasActiveAccess]

    def get_access_target(self):
        lesson = get_lesson_or_404(lesson_id=self.kwargs["lesson_id"])
        return {"course": lesson.module.course}

    @extend_schema(tags=["Me"], request=None, responses=MeLessonProgressWriteSerializer)
    def post(self, request, lesson_id):
        lesson = get_lesson_or_404(lesson_id=lesson_id)
        progress = record_lesson_view(user=request.user, lesson=lesson)
        return Response({"data": MeLessonProgressWriteSerializer(progress).data, "meta": {}})


class MeCourseProgressView(APIView):
    permission_classes = [HasActiveAccess]

    def get_access_target(self):
        return {"course": get_course_or_404(course_id=self.kwargs["course_id"])}

    @extend_schema(
        tags=["Me"],
        parameters=[OpenApiParameter("lang", str, description="Idioma de títulos (default: es)")],
    )
    def get(self, request, course_id):
        course = get_course_or_404(course_id=course_id)
        language = _lang(request)
        lessons = list(active_lessons_for_course(course=course, language=language))
        rows = progress_rows_for_course(user=request.user, course=course)
        total = len(lessons)
        completed = sum(
            1 for lesson in lessons if (rows.get(lesson.id) and rows[lesson.id].completed)
        )
        percent = int(round(100 * completed / total)) if total else 0
        items = []
        for lesson in lessons:
            row = rows.get(lesson.id)
            items.append(
                {
                    "id": str(lesson.id),
                    "module_id": str(lesson.module_id),
                    "title": get_active_translation(lesson, "title") or "",
                    "sort_order": lesson.sort_order,
                    "duration_seconds": lesson.duration_seconds,
                    "completed": bool(row and row.completed),
                    "completed_at": row.completed_at if row else None,
                    "last_viewed_at": row.last_viewed_at if row else None,
                }
            )
        return Response(
            {
                "data": {
                    "course_id": str(course.id),
                    "total_lessons": total,
                    "completed_lessons": completed,
                    "percent": percent,
                    "continue_lesson": continue_lesson_payload(
                        user=request.user, course=course, language=language
                    ),
                    "lessons": items,
                },
                "meta": {},
            }
        )
