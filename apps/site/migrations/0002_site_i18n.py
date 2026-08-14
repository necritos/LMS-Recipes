import uuid

import django.db.models.deletion
from django.db import migrations, models


def copy_legacy_site_texts(apps, schema_editor):
    Language = apps.get_model("catalog", "Language")
    SiteSettings = apps.get_model("site", "SiteSettings")
    SiteSettingsTranslation = apps.get_model("site", "SiteSettingsTranslation")
    HomeSlider = apps.get_model("site", "HomeSlider")
    HomeSliderTranslation = apps.get_model("site", "HomeSliderTranslation")
    StartButton = apps.get_model("site", "StartButton")
    StartButtonTranslation = apps.get_model("site", "StartButtonTranslation")
    Testimonial = apps.get_model("site", "Testimonial")
    TestimonialTranslation = apps.get_model("site", "TestimonialTranslation")

    has_content = (
        SiteSettings.objects.exclude(about_title="", about_html="").exists()
        or HomeSlider.objects.exists()
        or StartButton.objects.exists()
        or Testimonial.objects.exists()
    )
    if not has_content:
        return

    language = (
        Language.objects.filter(code="es").first() or Language.objects.order_by("code").first()
    )
    if language is None:
        language = Language.objects.create(code="es", name="Español", is_active=True)

    for row in SiteSettings.objects.all():
        title = (row.about_title or "").strip()
        html = row.about_html or ""
        if not title and not html:
            continue
        SiteSettingsTranslation.objects.create(
            settings=row,
            language=language,
            about_title=title,
            about_html=html,
        )

    for slider in HomeSlider.objects.all():
        HomeSliderTranslation.objects.create(
            slider=slider,
            language=language,
            title=slider.title or "",
            text=slider.text or "",
            link=slider.link or "",
            link_text=slider.link_text or "",
        )

    for button in StartButton.objects.all():
        StartButtonTranslation.objects.create(
            button=button,
            language=language,
            title=button.title or "",
            link=button.link or "",
            link_text=button.link_text or "",
        )

    for item in Testimonial.objects.all():
        TestimonialTranslation.objects.create(
            testimonial=item,
            language=language,
            name=item.name or "",
            comment=item.comment or "",
        )


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
        ("site", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomeSliderTranslation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("text", models.TextField(blank=True)),
                ("link", models.CharField(blank=True, max_length=500)),
                ("link_text", models.CharField(blank=True, max_length=120)),
                (
                    "language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="slider_translations",
                        to="catalog.language",
                    ),
                ),
                (
                    "slider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="site.homeslider",
                    ),
                ),
            ],
            options={
                "ordering": ["language__code"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("slider", "language"),
                        name="uniq_slider_translation_lang",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="SiteSettingsTranslation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("about_title", models.CharField(blank=True, max_length=255)),
                ("about_html", models.TextField(blank=True)),
                (
                    "language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="site_settings_translations",
                        to="catalog.language",
                    ),
                ),
                (
                    "settings",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="site.sitesettings",
                    ),
                ),
            ],
            options={
                "ordering": ["language__code"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("settings", "language"),
                        name="uniq_site_settings_translation_lang",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="StartButtonTranslation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("link", models.CharField(blank=True, max_length=500)),
                ("link_text", models.CharField(blank=True, max_length=120)),
                (
                    "button",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="site.startbutton",
                    ),
                ),
                (
                    "language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="start_button_translations",
                        to="catalog.language",
                    ),
                ),
            ],
            options={
                "ordering": ["language__code"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("button", "language"),
                        name="uniq_start_button_translation_lang",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="TestimonialTranslation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("comment", models.TextField()),
                (
                    "language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="testimonial_translations",
                        to="catalog.language",
                    ),
                ),
                (
                    "testimonial",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="site.testimonial",
                    ),
                ),
            ],
            options={
                "ordering": ["language__code"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("testimonial", "language"),
                        name="uniq_testimonial_translation_lang",
                    )
                ],
            },
        ),
        migrations.RunPython(copy_legacy_site_texts, migrations.RunPython.noop),
        migrations.RemoveField(model_name="homeslider", name="link"),
        migrations.RemoveField(model_name="homeslider", name="link_text"),
        migrations.RemoveField(model_name="homeslider", name="text"),
        migrations.RemoveField(model_name="homeslider", name="title"),
        migrations.RemoveField(model_name="sitesettings", name="about_html"),
        migrations.RemoveField(model_name="sitesettings", name="about_title"),
        migrations.RemoveField(model_name="startbutton", name="link"),
        migrations.RemoveField(model_name="startbutton", name="link_text"),
        migrations.RemoveField(model_name="startbutton", name="title"),
        migrations.RemoveField(model_name="testimonial", name="comment"),
        migrations.RemoveField(model_name="testimonial", name="name"),
    ]
