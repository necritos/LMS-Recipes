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


def _page_fields(item: dict, *, prefix: str, prev) -> dict:
    title_key = f"{prefix}_title"
    html_key = f"{prefix}_html"
    prev_title = getattr(prev, title_key, "") if prev else ""
    prev_html = getattr(prev, html_key, "") if prev else ""
    title = (item.get(title_key) or "").strip() if title_key in item else prev_title
    html = item.get(html_key) or "" if html_key in item else prev_html
    return {title_key: title, html_key: html}


def upsert_settings_translations(*, settings, translations: list[dict]) -> None:
    existing = {
        row.language_id: row for row in settings.translations.select_related("language").all()
    }
    settings.translations.all().delete()
    lang_map = _get_language_map([item["language_code"] for item in translations])
    for item in translations:
        language = lang_map[item["language_code"].strip().lower()]
        prev = existing.get(language.id)
        fields = {
            **_page_fields(item, prefix="about", prev=prev),
            **_page_fields(item, prefix="terms", prev=prev),
            **_page_fields(item, prefix="privacy", prev=prev),
            **_page_fields(item, prefix="contracting", prev=prev),
        }
        SiteSettingsTranslation.objects.create(
            settings=settings,
            language=language,
            **fields,
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
