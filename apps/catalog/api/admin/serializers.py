from rest_framework import serializers

from apps.catalog.api.serializers_helpers import JSONTranslationsMixin, TranslationInputSerializer
from apps.catalog.models import (
    Category,
    CategoryTranslation,
    Course,
    CourseTranslation,
    Language,
    Recipe,
    RecipeTranslation,
)


class AdminLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ("id", "code", "name", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class AdminCategoryTranslationSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = CategoryTranslation
        fields = ("id", "language_code", "name", "description")


class AdminCategorySerializer(serializers.ModelSerializer):
    translations = AdminCategoryTranslationSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "slug",
            "sort_order",
            "is_active",
            "translations",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AdminCategoryWriteSerializer(JSONTranslationsMixin, serializers.Serializer):
    slug = serializers.SlugField(max_length=120)
    sort_order = serializers.IntegerField(min_value=0, default=0)
    is_active = serializers.BooleanField(default=True)
    translations = serializers.ListField(child=TranslationInputSerializer())


class AdminCourseTranslationSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = CourseTranslation
        fields = (
            "id",
            "language_code",
            "title",
            "description",
            "meta_title",
            "meta_description",
        )


class AdminCourseSerializer(serializers.ModelSerializer):
    translations = AdminCourseTranslationSerializer(many=True, read_only=True)
    category_id = serializers.UUIDField(source="category.id", read_only=True, default=None)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "slug",
            "category_id",
            "price",
            "access_days",
            "status",
            "sort_order",
            "cover_image_url",
            "translations",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_cover_image_url(self, obj) -> str | None:
        if not obj.cover_image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.cover_image.url)
        return obj.cover_image.url


class AdminCourseWriteSerializer(JSONTranslationsMixin, serializers.Serializer):
    slug = serializers.SlugField(max_length=160)
    category_id = serializers.UUIDField(required=False, allow_null=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    access_days = serializers.IntegerField(min_value=1, default=365)
    status = serializers.ChoiceField(choices=["draft", "published"], default="draft")
    sort_order = serializers.IntegerField(min_value=0, default=0)
    cover_image = serializers.ImageField(required=False, allow_null=True)
    translations = serializers.ListField(child=TranslationInputSerializer())


class AdminRecipeTranslationSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = RecipeTranslation
        fields = (
            "id",
            "language_code",
            "title",
            "description",
            "meta_title",
            "meta_description",
        )


class AdminRecipeSerializer(serializers.ModelSerializer):
    translations = AdminRecipeTranslationSerializer(many=True, read_only=True)
    category_id = serializers.UUIDField(source="category.id", read_only=True, default=None)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "slug",
            "category_id",
            "price",
            "access_type",
            "access_days",
            "status",
            "sort_order",
            "cover_image_url",
            "translations",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_cover_image_url(self, obj) -> str | None:
        if not obj.cover_image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.cover_image.url)
        return obj.cover_image.url


class AdminRecipeWriteSerializer(JSONTranslationsMixin, serializers.Serializer):
    slug = serializers.SlugField(max_length=160)
    category_id = serializers.UUIDField(required=False, allow_null=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    access_type = serializers.ChoiceField(choices=["lifetime", "timed"], default="lifetime")
    access_days = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    status = serializers.ChoiceField(choices=["draft", "published"], default="draft")
    sort_order = serializers.IntegerField(min_value=0, default=0)
    cover_image = serializers.ImageField(required=False, allow_null=True)
    translations = serializers.ListField(child=TranslationInputSerializer())
