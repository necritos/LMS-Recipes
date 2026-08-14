from rest_framework import serializers

from apps.site.models import (
    ContactMessage,
    HomeSlider,
    NewsletterSubscriber,
    SiteSettings,
    StartButton,
    Testimonial,
)


def file_url(obj_file, request) -> str | None:
    if not obj_file:
        return None
    url = obj_file.url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if request:
        return request.build_absolute_uri(url)
    return url


class PublicSliderSerializer(serializers.ModelSerializer):
    background_image_url = serializers.SerializerMethodField()

    class Meta:
        model = HomeSlider
        fields = (
            "id",
            "title",
            "text",
            "link",
            "link_text",
            "sort_order",
            "background_image_url",
        )

    def get_background_image_url(self, obj) -> str | None:
        return file_url(obj.background_image, self.context.get("request"))


class PublicStartButtonSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = StartButton
        fields = ("id", "color", "title", "link", "link_text", "sort_order", "image_url")

    def get_image_url(self, obj) -> str | None:
        return file_url(obj.image, self.context.get("request"))


class PublicTestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ("id", "stars", "comment", "name", "sort_order")


class PublicSiteSerializer(serializers.Serializer):
    about = serializers.DictField()
    contact_info = serializers.DictField()
    social = serializers.DictField()
    sliders = PublicSliderSerializer(many=True)
    start_buttons = PublicStartButtonSerializer(many=True)
    testimonials = PublicTestimonialSerializer(many=True)


class ContactCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    topic = serializers.CharField(max_length=255)
    message = serializers.CharField()


class NewsletterSubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class AdminSiteSettingsSerializer(serializers.ModelSerializer):
    firebase_configured = serializers.SerializerMethodField()
    storage_backend = serializers.SerializerMethodField()
    firebase_credentials_json = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = SiteSettings
        fields = (
            "id",
            "about_title",
            "about_html",
            "social_instagram",
            "social_tiktok",
            "social_facebook",
            "social_pinterest",
            "phone_1",
            "phone_2",
            "contact_email",
            "firebase_enabled",
            "firebase_project_id",
            "firebase_bucket",
            "firebase_configured",
            "storage_backend",
            "firebase_credentials_json",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "firebase_configured",
            "storage_backend",
        )

    def get_firebase_configured(self, obj) -> bool:
        return bool(obj.firebase_credentials_json.strip())

    def get_storage_backend(self, obj) -> str:
        from apps.common.storage import active_storage_kind

        return active_storage_kind()


class AdminSliderSerializer(serializers.ModelSerializer):
    background_image_url = serializers.SerializerMethodField()

    class Meta:
        model = HomeSlider
        fields = (
            "id",
            "title",
            "text",
            "link",
            "link_text",
            "sort_order",
            "is_active",
            "background_image",
            "background_image_url",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {"background_image": {"write_only": True, "required": False}}
        read_only_fields = ("id", "created_at", "updated_at", "background_image_url")

    def get_background_image_url(self, obj) -> str | None:
        return file_url(obj.background_image, self.context.get("request"))


class AdminStartButtonSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = StartButton
        fields = (
            "id",
            "color",
            "title",
            "link",
            "link_text",
            "sort_order",
            "is_active",
            "image",
            "image_url",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {"image": {"write_only": True, "required": False}}
        read_only_fields = ("id", "created_at", "updated_at", "image_url")

    def validate_color(self, value: str) -> str:
        raw = value.strip()
        if not raw.startswith("#") or len(raw) not in {4, 7}:
            raise serializers.ValidationError("Usa un color hexadecimal (#RGB o #RRGGBB).")
        return raw

    def get_image_url(self, obj) -> str | None:
        return file_url(obj.image, self.context.get("request"))


class AdminTestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = (
            "id",
            "stars",
            "comment",
            "name",
            "sort_order",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AdminContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = (
            "id",
            "name",
            "email",
            "topic",
            "message",
            "is_read",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "name", "email", "topic", "message", "created_at", "updated_at")


class AdminContactReadSerializer(serializers.Serializer):
    is_read = serializers.BooleanField()


class AdminNewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ("id", "email", "created_at")
        read_only_fields = fields
