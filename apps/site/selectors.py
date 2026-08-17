from django.db.models import Prefetch, Q, QuerySet

from apps.catalog.models import Language
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


def get_site_settings() -> SiteSettings:
    settings, _ = SiteSettings.objects.get_or_create(singleton_key="default")
    return settings


def _prefetch_lang(qs, translation_model, language: Language):
    return (
        qs.filter(translations__language=language)
        .distinct()
        .prefetch_related(
            Prefetch(
                "translations",
                queryset=translation_model.objects.filter(language=language),
                to_attr="active_translations",
            )
        )
    )


def public_sliders(*, language: Language) -> QuerySet[HomeSlider]:
    return _prefetch_lang(
        HomeSlider.objects.filter(is_active=True),
        HomeSliderTranslation,
        language,
    ).order_by("sort_order", "created_at")


def public_start_buttons(*, language: Language) -> QuerySet[StartButton]:
    return _prefetch_lang(
        StartButton.objects.filter(is_active=True),
        StartButtonTranslation,
        language,
    ).order_by("sort_order", "created_at")


def public_testimonials(*, language: Language) -> QuerySet[Testimonial]:
    return _prefetch_lang(
        Testimonial.objects.filter(is_active=True),
        TestimonialTranslation,
        language,
    ).order_by("sort_order", "created_at")


_EMPTY_PAGE = {"title": "", "html": ""}


def _text_page(row, *, title_attr: str, html_attr: str) -> dict:
    if row is None:
        return dict(_EMPTY_PAGE)
    return {"title": getattr(row, title_attr) or "", "html": getattr(row, html_attr) or ""}


def public_legal_pages(*, language: Language) -> dict:
    settings = get_site_settings()
    row = SiteSettingsTranslation.objects.filter(settings=settings, language=language).first()
    return {
        "about": _text_page(row, title_attr="about_title", html_attr="about_html"),
        "terms": _text_page(row, title_attr="terms_title", html_attr="terms_html"),
        "privacy": _text_page(row, title_attr="privacy_title", html_attr="privacy_html"),
        "contracting": _text_page(
            row, title_attr="contracting_title", html_attr="contracting_html"
        ),
    }


def public_about(*, language: Language) -> dict:
    return public_legal_pages(language=language)["about"]


def admin_contact_messages(*, is_read: bool | None = None) -> QuerySet[ContactMessage]:
    qs = ContactMessage.objects.all()
    if is_read is not None:
        qs = qs.filter(is_read=is_read)
    return qs


def admin_newsletter_subscribers(
    *,
    search: str = "",
    mailchimp_status: str = "",
) -> QuerySet[NewsletterSubscriber]:
    qs = NewsletterSubscriber.objects.all()
    if search:
        qs = qs.filter(Q(email__icontains=search) | Q(name__icontains=search))
    if mailchimp_status:
        qs = qs.filter(mailchimp_status=mailchimp_status)
    return qs
