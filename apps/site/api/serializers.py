from rest_framework import serializers

from apps.catalog.api.serializers_helpers import JSONTranslationsMixin, get_active_translation
from apps.site.models import (
    ContactMessage,
    HomeSlider,
    HomeSliderTranslation,
    NewsletterSubscriber,
    SiteSettings,
    SiteSettingsTranslation,
    StartButton,
    StartButtonTranslation,
    Testimonial,
    TestimonialTranslation,
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


class SiteTranslationInputSerializer(serializers.Serializer):
    language_code = serializers.CharField(max_length=10)
    title = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    text = serializers.CharField(required=False, allow_blank=True, default="")
    link = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")
    link_text = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")
    about_title = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    about_html = serializers.CharField(required=False, allow_blank=True, default="")
    html = serializers.CharField(required=False, allow_blank=True, default="")
    name = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")
    comment = serializers.CharField(required=False, allow_blank=True, default="")


class PublicSliderSerializer(serializers.ModelSerializer):
    background_image_url = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    link_text = serializers.SerializerMethodField()

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

    def get_title(self, obj) -> str:
        return get_active_translation(obj, "title")

    def get_text(self, obj) -> str:
        return get_active_translation(obj, "text")

    def get_link(self, obj) -> str:
        return get_active_translation(obj, "link")

    def get_link_text(self, obj) -> str:
        return get_active_translation(obj, "link_text")


class PublicStartButtonSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    link_text = serializers.SerializerMethodField()

    class Meta:
        model = StartButton
        fields = ("id", "color", "title", "link", "link_text", "sort_order", "image_url")

    def get_image_url(self, obj) -> str | None:
        return file_url(obj.image, self.context.get("request"))

    def get_title(self, obj) -> str:
        return get_active_translation(obj, "title")

    def get_link(self, obj) -> str:
        return get_active_translation(obj, "link")

    def get_link_text(self, obj) -> str:
        return get_active_translation(obj, "link_text")


class PublicTestimonialSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()

    class Meta:
        model = Testimonial
        fields = ("id", "stars", "comment", "name", "sort_order")

    def get_name(self, obj) -> str:
        return get_active_translation(obj, "name")

    def get_comment(self, obj) -> str:
        return get_active_translation(obj, "comment")


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
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    language = serializers.CharField(max_length=10)
    consent = serializers.BooleanField()
    tags = serializers.ListField(
        child=serializers.CharField(max_length=40),
        required=False,
        default=list,
        max_length=10,
    )


class AdminAboutTranslationSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = SiteSettingsTranslation
        fields = ("id", "language_code", "about_title", "about_html")


class AdminSiteSettingsSerializer(JSONTranslationsMixin, serializers.ModelSerializer):
    firebase_configured = serializers.SerializerMethodField()
    storage_backend = serializers.SerializerMethodField()
    firebase_credentials_json = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    translations = serializers.ListField(
        child=SiteTranslationInputSerializer(), required=False, write_only=True
    )

    class Meta:
        model = SiteSettings
        fields = (
            "id",
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
            "translations",
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

    def validate_translations(self, value):
        return value

    def get_firebase_configured(self, obj) -> bool:
        return bool(obj.firebase_credentials_json.strip())

    def get_storage_backend(self, obj) -> str:
        from apps.common.storage import active_storage_kind

        return active_storage_kind()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["translations"] = AdminAboutTranslationSerializer(
            instance.translations.all(), many=True
        ).data
        return data


class AdminBunnySettingsSerializer(serializers.ModelSerializer):
    bunny_configured = serializers.SerializerMethodField()
    bunny_api_configured = serializers.SerializerMethodField()
    bunny_api_key = serializers.CharField(write_only=True, required=False, allow_blank=True)
    bunny_token_key = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = SiteSettings
        fields = (
            "bunny_enabled",
            "bunny_library_id",
            "bunny_cdn_hostname",
            "bunny_token_ttl_seconds",
            "bunny_configured",
            "bunny_api_configured",
            "bunny_api_key",
            "bunny_token_key",
        )
        read_only_fields = ("bunny_configured", "bunny_api_configured")

    def get_bunny_configured(self, obj) -> bool:
        return bool(obj.bunny_library_id.strip()) and bool(obj.bunny_token_key.strip())

    def get_bunny_api_configured(self, obj) -> bool:
        return bool(obj.bunny_api_key.strip())


class AdminStripeSettingsSerializer(serializers.ModelSerializer):
    stripe_configured = serializers.SerializerMethodField()
    stripe_webhook_configured = serializers.SerializerMethodField()
    stripe_secret_key = serializers.CharField(write_only=True, required=False, allow_blank=True)
    stripe_webhook_secret = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = SiteSettings
        fields = (
            "stripe_enabled",
            "stripe_mode",
            "stripe_publishable_key",
            "stripe_success_url",
            "stripe_cancel_url",
            "stripe_currency",
            "stripe_configured",
            "stripe_webhook_configured",
            "stripe_secret_key",
            "stripe_webhook_secret",
        )
        read_only_fields = ("stripe_configured", "stripe_webhook_configured")

    def get_stripe_configured(self, obj) -> bool:
        return bool(
            obj.stripe_secret_key.strip()
            and obj.stripe_success_url.strip()
            and obj.stripe_cancel_url.strip()
        )

    def get_stripe_webhook_configured(self, obj) -> bool:
        return bool(obj.stripe_webhook_secret.strip())


class AdminMailchimpSettingsSerializer(serializers.ModelSerializer):
    mailchimp_configured = serializers.SerializerMethodField()
    mailchimp_transactional_configured = serializers.SerializerMethodField()
    mailchimp_server_prefix = serializers.SerializerMethodField()
    mailchimp_api_key = serializers.CharField(write_only=True, required=False, allow_blank=True)
    mailchimp_transactional_api_key = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    mailchimp_from_email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = SiteSettings
        fields = (
            "mailchimp_enabled",
            "mailchimp_audience_id",
            "mailchimp_audience_name",
            "mailchimp_language_category_id",
            "mailchimp_interest_es_id",
            "mailchimp_interest_sk_id",
            "mailchimp_web_tag_es",
            "mailchimp_web_tag_sk",
            "mailchimp_double_opt_in",
            "mailchimp_marketing_permission_ids",
            "mailchimp_from_email",
            "mailchimp_from_name",
            "mailchimp_configured",
            "mailchimp_transactional_configured",
            "mailchimp_server_prefix",
            "mailchimp_api_key",
            "mailchimp_transactional_api_key",
        )
        read_only_fields = (
            "mailchimp_configured",
            "mailchimp_transactional_configured",
            "mailchimp_server_prefix",
        )

    def get_mailchimp_configured(self, obj) -> bool:
        return bool(obj.mailchimp_api_key.strip()) and bool(obj.mailchimp_audience_id.strip())

    def get_mailchimp_transactional_configured(self, obj) -> bool:
        return bool(obj.mailchimp_transactional_api_key.strip())

    def get_mailchimp_server_prefix(self, obj) -> str:
        key = (obj.mailchimp_api_key or "").strip()
        if "-" not in key:
            return ""
        return key.rsplit("-", 1)[-1].strip().lower()


class AdminSliderTranslationSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = HomeSliderTranslation
        fields = ("id", "language_code", "title", "text", "link", "link_text")


class AdminSliderSerializer(JSONTranslationsMixin, serializers.ModelSerializer):
    background_image_url = serializers.SerializerMethodField()
    translations = serializers.ListField(
        child=SiteTranslationInputSerializer(), required=False, write_only=True
    )

    class Meta:
        model = HomeSlider
        fields = (
            "id",
            "sort_order",
            "is_active",
            "background_image",
            "background_image_url",
            "translations",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {"background_image": {"write_only": True, "required": False}}
        read_only_fields = ("id", "created_at", "updated_at", "background_image_url")

    def validate(self, attrs):
        if self.instance is None and not attrs.get("translations"):
            raise serializers.ValidationError(
                {"translations": "Debes incluir al menos una traducción."}
            )
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["translations"] = AdminSliderTranslationSerializer(
            instance.translations.all(), many=True
        ).data
        return data

    def get_background_image_url(self, obj) -> str | None:
        return file_url(obj.background_image, self.context.get("request"))


class AdminStartButtonTranslationSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = StartButtonTranslation
        fields = ("id", "language_code", "title", "link", "link_text")


class AdminStartButtonSerializer(JSONTranslationsMixin, serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    translations = serializers.ListField(
        child=SiteTranslationInputSerializer(), required=False, write_only=True
    )

    class Meta:
        model = StartButton
        fields = (
            "id",
            "color",
            "sort_order",
            "is_active",
            "image",
            "image_url",
            "translations",
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

    def validate(self, attrs):
        if self.instance is None and not attrs.get("translations"):
            raise serializers.ValidationError(
                {"translations": "Debes incluir al menos una traducción."}
            )
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["translations"] = AdminStartButtonTranslationSerializer(
            instance.translations.all(), many=True
        ).data
        return data

    def get_image_url(self, obj) -> str | None:
        return file_url(obj.image, self.context.get("request"))


class AdminTestimonialTranslationSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = TestimonialTranslation
        fields = ("id", "language_code", "name", "comment")


class AdminTestimonialSerializer(JSONTranslationsMixin, serializers.ModelSerializer):
    translations = serializers.ListField(
        child=SiteTranslationInputSerializer(), required=False, write_only=True
    )

    class Meta:
        model = Testimonial
        fields = (
            "id",
            "stars",
            "sort_order",
            "is_active",
            "translations",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        if self.instance is None and not attrs.get("translations"):
            raise serializers.ValidationError(
                {"translations": "Debes incluir al menos una traducción."}
            )
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["translations"] = AdminTestimonialTranslationSerializer(
            instance.translations.all(), many=True
        ).data
        return data


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
    mailchimp_synced = serializers.SerializerMethodField()
    mailchimp_destination = serializers.SerializerMethodField()
    tags = serializers.ListField(source="extra_tags", read_only=True)

    class Meta:
        model = NewsletterSubscriber
        fields = (
            "id",
            "email",
            "name",
            "language",
            "consent",
            "consented_at",
            "tags",
            "mailchimp_synced",
            "mailchimp_status",
            "mailchimp_synced_at",
            "mailchimp_audience_id",
            "mailchimp_audience_name",
            "mailchimp_group",
            "mailchimp_tags",
            "mailchimp_destination",
            "mailchimp_error",
            "created_at",
        )
        read_only_fields = fields

    def get_mailchimp_synced(self, obj) -> bool:
        return obj.mailchimp_status == NewsletterSubscriber.MailchimpStatus.SYNCED

    def get_mailchimp_destination(self, obj) -> str:
        if obj.mailchimp_status == NewsletterSubscriber.MailchimpStatus.SKIPPED:
            return ""
        parts = []
        audience = obj.mailchimp_audience_name or obj.mailchimp_audience_id
        if audience:
            if obj.mailchimp_audience_id and obj.mailchimp_audience_name:
                parts.append(f"{obj.mailchimp_audience_name} ({obj.mailchimp_audience_id})")
            else:
                parts.append(audience)
        if obj.mailchimp_group:
            parts.append(f"Idioma: {obj.mailchimp_group}")
        tags = obj.mailchimp_tags or []
        if tags:
            parts.append("tags: " + ", ".join(tags))
        return " · ".join(parts)
