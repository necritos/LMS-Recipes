from django.contrib import admin

from apps.site.models import (
    ContactMessage,
    HomeSlider,
    NewsletterSubscriber,
    SiteSettings,
    StartButton,
    Testimonial,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("singleton_key", "firebase_enabled", "contact_email", "updated_at")


@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active")


@admin.register(StartButton)
class StartButtonAdmin(admin.ModelAdmin):
    list_display = ("title", "color", "sort_order", "is_active")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "stars", "sort_order", "is_active")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("email", "topic", "is_read", "created_at")
    list_filter = ("is_read",)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at")
    search_fields = ("email",)
