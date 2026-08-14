from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.selectors import get_active_language, resolve_language_code
from apps.common.permissions import HasActiveAccess
from apps.content.api.me.serializers import MeModuleSerializer
from apps.content.selectors import get_course_or_404, get_recipe_or_404, player_modules_for_course
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
