from rest_framework import serializers

from apps.catalog.api.serializers_helpers import get_active_translation
from apps.catalog.models import Category, Course, Language, Recipe


class PublicLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ("id", "code", "name")


class PublicCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "slug", "name", "description", "sort_order")

    def get_name(self, obj) -> str:
        return get_active_translation(obj, "name")

    def get_description(self, obj) -> str:
        return get_active_translation(obj, "description")


class PublicCourseListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    category_slug = serializers.CharField(source="category.slug", default=None)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "slug",
            "title",
            "description",
            "price",
            "access_days",
            "category_slug",
            "cover_image_url",
        )

    def get_title(self, obj) -> str:
        return get_active_translation(obj, "title")

    def get_description(self, obj) -> str:
        return get_active_translation(obj, "description")

    def get_cover_image_url(self, obj) -> str | None:
        if obj.cover_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return None


class PublicCourseDetailSerializer(PublicCourseListSerializer):
    meta_title = serializers.SerializerMethodField()
    meta_description = serializers.SerializerMethodField()

    class Meta(PublicCourseListSerializer.Meta):
        fields = PublicCourseListSerializer.Meta.fields + (
            "meta_title",
            "meta_description",
            "status",
        )

    def get_meta_title(self, obj) -> str:
        return get_active_translation(obj, "meta_title")

    def get_meta_description(self, obj) -> str:
        return get_active_translation(obj, "meta_description")


class PublicRecipeListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    category_slug = serializers.CharField(source="category.slug", default=None)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "slug",
            "title",
            "description",
            "price",
            "access_type",
            "access_days",
            "category_slug",
            "cover_image_url",
        )

    def get_title(self, obj) -> str:
        return get_active_translation(obj, "title")

    def get_description(self, obj) -> str:
        return get_active_translation(obj, "description")

    def get_cover_image_url(self, obj) -> str | None:
        if obj.cover_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return None


class PublicRecipeDetailSerializer(PublicRecipeListSerializer):
    meta_title = serializers.SerializerMethodField()
    meta_description = serializers.SerializerMethodField()

    class Meta(PublicRecipeListSerializer.Meta):
        fields = PublicRecipeListSerializer.Meta.fields + (
            "meta_title",
            "meta_description",
            "status",
        )

    def get_meta_title(self, obj) -> str:
        return get_active_translation(obj, "meta_title")

    def get_meta_description(self, obj) -> str:
        return get_active_translation(obj, "meta_description")
