from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel, UUIDModel


def site_image_upload_path(instance, filename: str) -> str:
    folder = instance.__class__.__name__.lower()
    return f"site/{folder}/{instance.pk or 'new'}/{filename}"


class SiteSettings(UUIDModel, TimeStampedModel):
    singleton_key = models.CharField(max_length=16, unique=True, default="default")

    about_title = models.CharField(max_length=255, blank=True)
    about_html = models.TextField(blank=True)

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

    class Meta:
        verbose_name = "site settings"
        verbose_name_plural = "site settings"

    def __str__(self) -> str:
        return "Site settings"


class HomeSlider(UUIDModel, TimeStampedModel):
    background_image = models.ImageField(upload_to=site_image_upload_path, blank=True)
    title = models.CharField(max_length=255)
    text = models.TextField(blank=True)
    link = models.CharField(max_length=500, blank=True)
    link_text = models.CharField(max_length=120, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self) -> str:
        return self.title


class StartButton(UUIDModel, TimeStampedModel):
    color = models.CharField(max_length=7, default="#000000")
    image = models.ImageField(upload_to=site_image_upload_path, blank=True)
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=500, blank=True)
    link_text = models.CharField(max_length=120, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self) -> str:
        return self.title


class Testimonial(UUIDModel, TimeStampedModel):
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    name = models.CharField(max_length=200)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self) -> str:
        return self.name


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
    email = models.EmailField(unique=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email
