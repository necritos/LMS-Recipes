from rest_framework import serializers

from apps.catalog.api.serializers_helpers import JSONTranslationsMixin, TranslationInputSerializer
from apps.catalog.models import (
    Category,
    CategoryTranslation,
    Course,
    CourseResource,
    CourseResourceTranslation,
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
            "format",
            "event_starts_at",
            "event_address",
            "maps_url",
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
    format = serializers.ChoiceField(choices=["online", "in_person"], required=False)
    event_starts_at = serializers.DateTimeField(required=False, allow_null=True)
    event_address = serializers.CharField(required=False, allow_blank=True, max_length=500)
    maps_url = serializers.URLField(required=False, allow_blank=True, max_length=1000)
    status = serializers.ChoiceField(choices=["draft", "published"], default="draft")
    sort_order = serializers.IntegerField(min_value=0, default=0)
    cover_image = serializers.ImageField(required=False, allow_null=True)
    translations = serializers.ListField(child=TranslationInputSerializer())


class AdminCourseResourceTranslationSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = CourseResourceTranslation
        fields = ("id", "language_code", "title", "description")


class AdminCourseResourceSerializer(serializers.ModelSerializer):
    translations = AdminCourseResourceTranslationSerializer(many=True, read_only=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = CourseResource
        fields = (
            "id",
            "course_id",
            "kind",
            "original_name",
            "content_type",
            "sort_order",
            "is_active",
            "download_url",
            "translations",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "course_id", "created_at", "updated_at")

    def get_download_url(self, obj) -> str | None:
        request = self.context.get("request")
        if not request or not obj.file:
            return None
        return request.build_absolute_uri(f"/api/v1/admin/resources/{obj.id}/file/")


class AdminCourseResourceWriteSerializer(JSONTranslationsMixin, serializers.Serializer):
    file = serializers.FileField(required=False)
    kind = serializers.ChoiceField(choices=["pdf", "image", "file"], required=False)
    sort_order = serializers.IntegerField(min_value=0, default=0)
    is_active = serializers.BooleanField(default=True)
    translations = serializers.ListField(child=TranslationInputSerializer(), required=False)

    def validate(self, attrs):
        creating = self.context.get("creating", False)
        if creating and not attrs.get("file"):
            raise serializers.ValidationError({"file": "Debes subir un archivo."})
        if creating and not attrs.get("translations"):
            raise serializers.ValidationError(
                {"translations": "Debes incluir al menos una traducción."}
            )
        return attrs


class AdminCoursePurchaseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.SerializerMethodField()
    order_id = serializers.UUIDField(read_only=True)
    paid_at = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    expires_at = serializers.SerializerMethodField()
    is_lifetime = serializers.SerializerMethodField()

    def get_user(self, obj) -> dict:
        user = obj.user
        full_name = f"{user.first_name} {user.last_name}".strip() or user.email
        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": full_name,
        }

    def get_paid_at(self, obj):
        return obj.order.paid_at if obj.order_id else None

    def get_expires_at(self, obj):
        grant = obj.access_grant
        return grant.expires_at if grant else None

    def get_is_lifetime(self, obj) -> bool:
        grant = obj.access_grant
        return grant is not None and grant.expires_at is None


class AdminRecipeTranslationSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = RecipeTranslation
        fields = (
            "id",
            "language_code",
            "title",
            "description",
            "ingredients_html",
            "preparation_html",
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
            "bunny_video_id",
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
    bunny_video_id = serializers.CharField(required=False, allow_blank=True, default="")
    translations = serializers.ListField(child=TranslationInputSerializer())
