from rest_framework import serializers

from apps.catalog.api.serializers_helpers import JSONTranslationsMixin, TranslationInputSerializer
from apps.content.models import Lesson, LessonTranslation, Module, ModuleTranslation


class AdminModuleTranslationSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = ModuleTranslation
        fields = ("id", "language_code", "title", "description")


class AdminLessonTranslationSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = LessonTranslation
        fields = ("id", "language_code", "title", "description", "content_html")


class AdminLessonSerializer(JSONTranslationsMixin, serializers.ModelSerializer):
    translations = serializers.ListField(
        child=TranslationInputSerializer(), required=False, write_only=True
    )

    class Meta:
        model = Lesson
        fields = (
            "id",
            "module_id",
            "bunny_video_id",
            "duration_seconds",
            "sort_order",
            "is_active",
            "translations",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "module_id", "created_at", "updated_at")

    def validate(self, attrs):
        if self.instance is None and not attrs.get("translations"):
            raise serializers.ValidationError(
                {"translations": "Debes incluir al menos una traducción."}
            )
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["translations"] = AdminLessonTranslationSerializer(
            instance.translations.all(), many=True
        ).data
        return data


class AdminModuleSerializer(JSONTranslationsMixin, serializers.ModelSerializer):
    translations = serializers.ListField(
        child=TranslationInputSerializer(), required=False, write_only=True
    )
    lessons = AdminLessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = (
            "id",
            "course_id",
            "sort_order",
            "is_active",
            "translations",
            "lessons",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "course_id", "lessons", "created_at", "updated_at")

    def validate(self, attrs):
        if self.instance is None and not attrs.get("translations"):
            raise serializers.ValidationError(
                {"translations": "Debes incluir al menos una traducción."}
            )
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["translations"] = AdminModuleTranslationSerializer(
            instance.translations.all(), many=True
        ).data
        return data
