from django.db import transaction

from apps.site.models import HomeSlider, StartButton, Testimonial
from apps.site.services.i18n import (
    upsert_slider_translations,
    upsert_start_button_translations,
    upsert_testimonial_translations,
)


@transaction.atomic
def create_slider(*, translations: list[dict] | None = None, **fields) -> HomeSlider:
    slider = HomeSlider.objects.create(**fields)
    upsert_slider_translations(slider=slider, translations=translations)
    return slider


@transaction.atomic
def update_slider(*, slider: HomeSlider, **fields) -> HomeSlider:
    translations = fields.pop("translations", None)
    for key, value in fields.items():
        setattr(slider, key, value)
    slider.save()
    if translations is not None:
        upsert_slider_translations(slider=slider, translations=translations)
    return slider


@transaction.atomic
def delete_slider(*, slider: HomeSlider) -> None:
    slider.delete()


@transaction.atomic
def create_start_button(*, translations: list[dict] | None = None, **fields) -> StartButton:
    button = StartButton.objects.create(**fields)
    upsert_start_button_translations(button=button, translations=translations)
    return button


@transaction.atomic
def update_start_button(*, button: StartButton, **fields) -> StartButton:
    translations = fields.pop("translations", None)
    for key, value in fields.items():
        setattr(button, key, value)
    button.save()
    if translations is not None:
        upsert_start_button_translations(button=button, translations=translations)
    return button


@transaction.atomic
def delete_start_button(*, button: StartButton) -> None:
    button.delete()


@transaction.atomic
def create_testimonial(*, translations: list[dict] | None = None, **fields) -> Testimonial:
    item = Testimonial.objects.create(**fields)
    upsert_testimonial_translations(testimonial=item, translations=translations)
    return item


@transaction.atomic
def update_testimonial(*, testimonial: Testimonial, **fields) -> Testimonial:
    translations = fields.pop("translations", None)
    for key, value in fields.items():
        setattr(testimonial, key, value)
    testimonial.save()
    if translations is not None:
        upsert_testimonial_translations(testimonial=testimonial, translations=translations)
    return testimonial


@transaction.atomic
def delete_testimonial(*, testimonial: Testimonial) -> None:
    testimonial.delete()
