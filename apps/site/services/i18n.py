from apps.catalog.services.category_service import _get_language_map
from apps.common.exceptions import BusinessError
from apps.site.models import (
    HomeSlider,
    HomeSliderTranslation,
    SiteSettingsTranslation,
    StartButton,
    StartButtonTranslation,
    Testimonial,
    TestimonialTranslation,
)


def _require_translations(translations: list[dict] | None) -> list[dict]:
    if not translations:
        raise BusinessError(
            "TRANSLATIONS_REQUIRED",
            "Debes incluir al menos una traducción.",
            http_status=422,
        )
    return translations


def upsert_settings_translations(*, settings, translations: list[dict]) -> None:
    settings.translations.all().delete()
    lang_map = _get_language_map([item["language_code"] for item in translations])
    for item in translations:
        language = lang_map[item["language_code"].strip().lower()]
        SiteSettingsTranslation.objects.create(
            settings=settings,
            language=language,
            about_title=(item.get("about_title") or item.get("title") or "").strip(),
            about_html=item.get("about_html") or item.get("html") or "",
        )


def upsert_slider_translations(*, slider: HomeSlider, translations: list[dict]) -> None:
    translations = _require_translations(translations)
    slider.translations.all().delete()
    lang_map = _get_language_map([item["language_code"] for item in translations])
    for item in translations:
        language = lang_map[item["language_code"].strip().lower()]
        title = (item.get("title") or "").strip()
        if not title:
            raise BusinessError(
                "TRANSLATION_TITLE_REQUIRED",
                "Cada traducción del slider necesita title.",
                http_status=422,
            )
        HomeSliderTranslation.objects.create(
            slider=slider,
            language=language,
            title=title,
            text=item.get("text") or "",
            link=item.get("link") or "",
            link_text=item.get("link_text") or "",
        )


def upsert_start_button_translations(*, button: StartButton, translations: list[dict]) -> None:
    translations = _require_translations(translations)
    button.translations.all().delete()
    lang_map = _get_language_map([item["language_code"] for item in translations])
    for item in translations:
        language = lang_map[item["language_code"].strip().lower()]
        title = (item.get("title") or "").strip()
        if not title:
            raise BusinessError(
                "TRANSLATION_TITLE_REQUIRED",
                "Cada traducción del botón necesita title.",
                http_status=422,
            )
        StartButtonTranslation.objects.create(
            button=button,
            language=language,
            title=title,
            link=item.get("link") or "",
            link_text=item.get("link_text") or "",
        )


def upsert_testimonial_translations(*, testimonial: Testimonial, translations: list[dict]) -> None:
    translations = _require_translations(translations)
    testimonial.translations.all().delete()
    lang_map = _get_language_map([item["language_code"] for item in translations])
    for item in translations:
        language = lang_map[item["language_code"].strip().lower()]
        name = (item.get("name") or "").strip()
        comment = (item.get("comment") or "").strip()
        if not name or not comment:
            raise BusinessError(
                "TRANSLATION_FIELDS_REQUIRED",
                "Cada traducción de referencia necesita name y comment.",
                http_status=422,
            )
        TestimonialTranslation.objects.create(
            testimonial=testimonial,
            language=language,
            name=name,
            comment=comment,
        )
