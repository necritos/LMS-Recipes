from django.contrib import admin

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


class SiteSettingsTranslationInline(admin.TabularInline):
    model = SiteSettingsTranslation
    extra = 1


class HomeSliderTranslationInline(admin.TabularInline):
    model = HomeSliderTranslation
    extra = 1


class StartButtonTranslationInline(admin.TabularInline):
    model = StartButtonTranslation
    extra = 1


class TestimonialTranslationInline(admin.TabularInline):
    model = TestimonialTranslation
    extra = 1


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "singleton_key",
        "firebase_enabled",
        "bunny_enabled",
        "stripe_enabled",
        "mailchimp_enabled",
        "contact_email",
        "updated_at",
    )
    inlines = [SiteSettingsTranslationInline]
    exclude = (
        "firebase_credentials_json",
        "bunny_api_key",
        "bunny_token_key",
        "stripe_secret_key",
        "stripe_webhook_secret",
        "mailchimp_api_key",
        "mailchimp_transactional_api_key",
    )


@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ("id", "sort_order", "is_active")
    inlines = [HomeSliderTranslationInline]


@admin.register(StartButton)
class StartButtonAdmin(admin.ModelAdmin):
    list_display = ("id", "color", "sort_order", "is_active")
    inlines = [StartButtonTranslationInline]


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("id", "stars", "sort_order", "is_active")
    inlines = [TestimonialTranslationInline]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("email", "topic", "is_read", "created_at")
    list_filter = ("is_read",)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "name",
        "language",
        "mailchimp_status",
        "mailchimp_audience_name",
        "mailchimp_group",
        "created_at",
    )
    search_fields = ("email", "name")
    list_filter = ("mailchimp_status", "language", "consent")
