from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.catalog.models import Language
from apps.common.models import TimeStampedModel, UUIDModel


def site_image_upload_path(instance, filename: str) -> str:
    folder = instance.__class__.__name__.lower()
    return f"site/{folder}/{instance.pk or 'new'}/{filename}"


class SiteSettings(UUIDModel, TimeStampedModel):
    singleton_key = models.CharField(max_length=16, unique=True, default="default")

    social_instagram = models.CharField(max_length=500, blank=True)
    social_tiktok = models.CharField(max_length=500, blank=True)
    social_facebook = models.CharField(max_length=500, blank=True)
    social_pinterest = models.CharField(max_length=500, blank=True)

    phone_1 = models.CharField(max_length=50, blank=True)
    phone_2 = models.CharField(max_length=50, blank=True)
    contact_email = models.EmailField(blank=True)

    firebase_enabled = models.BooleanField(default=False)
    firebase_project_id = models.CharField(max_length=200, blank=True)
    firebase_bucket = models.CharField(max_length=255, blank=True)
    firebase_credentials_json = models.TextField(blank=True)

    bunny_enabled = models.BooleanField(default=False)
    bunny_library_id = models.CharField(max_length=64, blank=True)
    bunny_cdn_hostname = models.CharField(max_length=255, blank=True)
    bunny_api_key = models.TextField(blank=True)
    bunny_token_key = models.TextField(blank=True)
    bunny_token_ttl_seconds = models.PositiveIntegerField(default=3600)

    stripe_enabled = models.BooleanField(default=False)
    stripe_mode = models.CharField(max_length=10, default="test")
    stripe_publishable_key = models.CharField(max_length=255, blank=True)
    stripe_secret_key = models.TextField(blank=True)
    stripe_webhook_secret = models.TextField(blank=True)
    stripe_success_url = models.CharField(max_length=500, blank=True)
    stripe_cancel_url = models.CharField(max_length=500, blank=True)
    stripe_currency = models.CharField(max_length=3, default="eur")

    mailchimp_enabled = models.BooleanField(default=False)
    mailchimp_api_key = models.TextField(blank=True)
    mailchimp_audience_id = models.CharField(max_length=32, blank=True)
    mailchimp_audience_name = models.CharField(max_length=120, blank=True)
    mailchimp_language_category_id = models.CharField(max_length=64, blank=True)
    mailchimp_interest_es_id = models.CharField(max_length=64, blank=True)
    mailchimp_interest_sk_id = models.CharField(max_length=64, blank=True)
    mailchimp_web_tag_es = models.CharField(max_length=40, default="WEB_ES")
    mailchimp_web_tag_sk = models.CharField(max_length=40, default="WEB_SK")
    mailchimp_double_opt_in = models.BooleanField(default=False)
    mailchimp_marketing_permission_ids = models.CharField(max_length=500, blank=True)
    mailchimp_transactional_api_key = models.TextField(blank=True)
    mailchimp_from_email = models.EmailField(blank=True)
    mailchimp_from_name = models.CharField(max_length=120, blank=True)

    google_oauth_enabled = models.BooleanField(default=False)
    google_client_id = models.CharField(max_length=255, blank=True)
    google_client_secret = models.TextField(blank=True)

    class Meta:
        verbose_name = "site settings"
        verbose_name_plural = "site settings"

    def __str__(self) -> str:
        return "Site settings"


class SiteSettingsTranslation(UUIDModel, TimeStampedModel):
    settings = models.ForeignKey(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name="translations",
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name="site_settings_translations",
    )
    about_title = models.CharField(max_length=255, blank=True)
    about_html = models.TextField(blank=True)
    terms_title = models.CharField(max_length=255, blank=True)
    terms_html = models.TextField(blank=True)
    privacy_title = models.CharField(max_length=255, blank=True)
    privacy_html = models.TextField(blank=True)
    contracting_title = models.CharField(max_length=255, blank=True)
    contracting_html = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["settings", "language"],
                name="uniq_site_settings_translation_lang",
            )
        ]
        ordering = ["language__code"]

    def __str__(self) -> str:
        return f"about [{self.language.code}]"


class HomeSlider(UUIDModel, TimeStampedModel):
    background_image = models.ImageField(upload_to=site_image_upload_path, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self) -> str:
        return f"slider {self.pk}"


class HomeSliderTranslation(UUIDModel, TimeStampedModel):
    slider = models.ForeignKey(HomeSlider, on_delete=models.CASCADE, related_name="translations")
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name="slider_translations",
    )
    title = models.CharField(max_length=255)
    text = models.TextField(blank=True)
    link = models.CharField(max_length=500, blank=True)
    link_text = models.CharField(max_length=120, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["slider", "language"], name="uniq_slider_translation_lang"
            )
        ]
        ordering = ["language__code"]

    def __str__(self) -> str:
        return f"{self.title} [{self.language.code}]"


class StartButton(UUIDModel, TimeStampedModel):
    color = models.CharField(max_length=7, default="#000000")
    image = models.ImageField(upload_to=site_image_upload_path, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self) -> str:
        return f"start-button {self.pk}"


class StartButtonTranslation(UUIDModel, TimeStampedModel):
    button = models.ForeignKey(StartButton, on_delete=models.CASCADE, related_name="translations")
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name="start_button_translations",
    )
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=500, blank=True)
    link_text = models.CharField(max_length=120, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["button", "language"],
                name="uniq_start_button_translation_lang",
            )
        ]
        ordering = ["language__code"]

    def __str__(self) -> str:
        return f"{self.title} [{self.language.code}]"


class Testimonial(UUIDModel, TimeStampedModel):
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self) -> str:
        return f"testimonial {self.pk}"


class TestimonialTranslation(UUIDModel, TimeStampedModel):
    testimonial = models.ForeignKey(
        Testimonial,
        on_delete=models.CASCADE,
        related_name="translations",
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name="testimonial_translations",
    )
    name = models.CharField(max_length=200)
    comment = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["testimonial", "language"],
                name="uniq_testimonial_translation_lang",
            )
        ]
        ordering = ["language__code"]

    def __str__(self) -> str:
        return f"{self.name} [{self.language.code}]"


class ContactMessage(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    topic = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["is_read", "-created_at"]

    def __str__(self) -> str:
        return f"{self.email} — {self.topic}"


class NewsletterSubscriber(UUIDModel, TimeStampedModel):
    class MailchimpStatus(models.TextChoices):
        PENDING = "pending", "Pendiente"
        SYNCED = "synced", "Sincronizado"
        FAILED = "failed", "Error"
        SKIPPED = "skipped", "Omitido"

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True)
    language = models.CharField(max_length=10, blank=True)
    consent = models.BooleanField(default=False)
    consented_at = models.DateTimeField(null=True, blank=True)
    extra_tags = models.JSONField(default=list, blank=True)
    mailchimp_status = models.CharField(
        max_length=16,
        choices=MailchimpStatus.choices,
        default=MailchimpStatus.SKIPPED,
    )
    mailchimp_synced_at = models.DateTimeField(null=True, blank=True)
    mailchimp_audience_id = models.CharField(max_length=32, blank=True)
    mailchimp_audience_name = models.CharField(max_length=120, blank=True)
    mailchimp_group = models.CharField(max_length=80, blank=True)
    mailchimp_tags = models.JSONField(default=list, blank=True)
    mailchimp_error = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email
