from django.db.models import QuerySet

from apps.site.models import (
    ContactMessage,
    HomeSlider,
    NewsletterSubscriber,
    SiteSettings,
    StartButton,
    Testimonial,
)


def get_site_settings() -> SiteSettings:
    settings, _ = SiteSettings.objects.get_or_create(singleton_key="default")
    return settings


def public_sliders() -> QuerySet[HomeSlider]:
    return HomeSlider.objects.filter(is_active=True).order_by("sort_order", "created_at")


def public_start_buttons() -> QuerySet[StartButton]:
    return StartButton.objects.filter(is_active=True).order_by("sort_order", "created_at")


def public_testimonials() -> QuerySet[Testimonial]:
    return Testimonial.objects.filter(is_active=True).order_by("sort_order", "created_at")


def admin_sliders() -> QuerySet[HomeSlider]:
    return HomeSlider.objects.all()


def admin_start_buttons() -> QuerySet[StartButton]:
    return StartButton.objects.all()


def admin_testimonials() -> QuerySet[Testimonial]:
    return Testimonial.objects.all()


def admin_contact_messages(*, is_read: bool | None = None) -> QuerySet[ContactMessage]:
    qs = ContactMessage.objects.all()
    if is_read is not None:
        qs = qs.filter(is_read=is_read)
    return qs


def admin_newsletter_subscribers(*, search: str = "") -> QuerySet[NewsletterSubscriber]:
    qs = NewsletterSubscriber.objects.all()
    if search:
        qs = qs.filter(email__icontains=search)
    return qs
