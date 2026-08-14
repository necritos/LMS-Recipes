from django.utils import timezone
from rest_framework import serializers

from apps.catalog.api.serializers_helpers import get_active_translation
from apps.content.models import AccessGrant, Lesson, LessonProgress, Module
from apps.content.selectors import continue_lesson_for_course


def _cover_url(obj, request) -> str | None:
    if obj is None or not obj.cover_image:
        return None
    if request:
        return request.build_absolute_uri(obj.cover_image.url)
    return obj.cover_image.url


def continue_lesson_payload(*, user, course, language=None) -> dict | None:
    lesson = continue_lesson_for_course(user=user, course=course, language=language)
    if lesson is None:
        return None
    return {
        "id": str(lesson.id),
        "module_id": str(lesson.module_id),
        "title": get_active_translation(lesson, "title") or "",
        "sort_order": lesson.sort_order,
    }


class MeLessonSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ("id", "title", "duration_seconds", "sort_order", "video")

    def get_title(self, obj) -> str:
        return get_active_translation(obj, "title")

    def get_video(self, obj):
        videos = self.context.get("signed_videos") or {}
        return videos.get(str(obj.pk))


class MeModuleSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    lessons = MeLessonSerializer(many=True)

    class Meta:
        model = Module
        fields = ("id", "title", "sort_order", "lessons")

    def get_title(self, obj) -> str:
        return get_active_translation(obj, "title")


class PublicCurriculumLessonSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ("id", "title", "duration_seconds", "sort_order")

    def get_title(self, obj) -> str:
        return get_active_translation(obj, "title")


class PublicCurriculumModuleSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    lessons = PublicCurriculumLessonSerializer(many=True)

    class Meta:
        model = Module
        fields = ("id", "title", "sort_order", "lessons")

    def get_title(self, obj) -> str:
        return get_active_translation(obj, "title")


class MeAccessSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    is_lifetime = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = AccessGrant
        fields = (
            "id",
            "product_id",
            "slug",
            "title",
            "cover_image_url",
            "expires_at",
            "is_lifetime",
            "is_active",
        )

    def _product(self, obj):
        return obj.course or obj.recipe

    def get_product_id(self, obj) -> str:
        return str(self._product(obj).id)

    def get_slug(self, obj) -> str:
        return self._product(obj).slug

    def get_title(self, obj) -> str:
        product = self._product(obj)
        return get_active_translation(product, "title") or product.slug

    def get_cover_image_url(self, obj) -> str | None:
        return _cover_url(self._product(obj), self.context.get("request"))

    def get_is_lifetime(self, obj) -> bool:
        return obj.expires_at is None

    def get_is_active(self, obj) -> bool:
        if obj.is_revoked:
            return False
        return obj.expires_at is None or obj.expires_at > timezone.now()


class MeCourseAccessSerializer(MeAccessSerializer):
    access_days = serializers.SerializerMethodField()
    continue_lesson = serializers.SerializerMethodField()

    class Meta(MeAccessSerializer.Meta):
        fields = MeAccessSerializer.Meta.fields + ("access_days", "continue_lesson")

    def get_access_days(self, obj) -> int | None:
        return obj.course.access_days if obj.course_id else None

    def get_continue_lesson(self, obj) -> dict | None:
        return continue_lesson_payload(
            user=self.context["request"].user,
            course=obj.course,
            language=self.context.get("language"),
        )


class MeRecipeAccessSerializer(MeAccessSerializer):
    access_type = serializers.SerializerMethodField()
    access_days = serializers.SerializerMethodField()

    class Meta(MeAccessSerializer.Meta):
        fields = MeAccessSerializer.Meta.fields + ("access_type", "access_days")

    def get_access_type(self, obj) -> str | None:
        return obj.recipe.access_type if obj.recipe_id else None

    def get_access_days(self, obj) -> int | None:
        return obj.recipe.access_days if obj.recipe_id else None


class MeLessonProgressWriteSerializer(serializers.ModelSerializer):
    lesson_id = serializers.SerializerMethodField()

    class Meta:
        model = LessonProgress
        fields = ("lesson_id", "completed", "completed_at", "last_viewed_at")

    def get_lesson_id(self, obj) -> str:
        return str(obj.lesson_id)
