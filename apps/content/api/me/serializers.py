from rest_framework import serializers

from apps.catalog.api.serializers_helpers import get_active_translation
from apps.content.models import Lesson, Module


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
