from django.db import transaction

from apps.site.models import HomeSlider, StartButton, Testimonial


@transaction.atomic
def create_slider(**fields) -> HomeSlider:
    return HomeSlider.objects.create(**fields)


@transaction.atomic
def update_slider(*, slider: HomeSlider, **fields) -> HomeSlider:
    for key, value in fields.items():
        setattr(slider, key, value)
    slider.save()
    return slider


@transaction.atomic
def delete_slider(*, slider: HomeSlider) -> None:
    slider.delete()


@transaction.atomic
def create_start_button(**fields) -> StartButton:
    return StartButton.objects.create(**fields)


@transaction.atomic
def update_start_button(*, button: StartButton, **fields) -> StartButton:
    for key, value in fields.items():
        setattr(button, key, value)
    button.save()
    return button


@transaction.atomic
def delete_start_button(*, button: StartButton) -> None:
    button.delete()


@transaction.atomic
def create_testimonial(**fields) -> Testimonial:
    return Testimonial.objects.create(**fields)


@transaction.atomic
def update_testimonial(*, testimonial: Testimonial, **fields) -> Testimonial:
    for key, value in fields.items():
        setattr(testimonial, key, value)
    testimonial.save()
    return testimonial


@transaction.atomic
def delete_testimonial(*, testimonial: Testimonial) -> None:
    testimonial.delete()
