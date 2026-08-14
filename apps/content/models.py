from django.db import models

from apps.accounts.models import UserAccount
from apps.catalog.models import Course, Language, Recipe
from apps.common.models import TimeStampedModel, UUIDModel


class Module(UUIDModel, TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self) -> str:
        return f"module {self.pk}"


class ModuleTranslation(UUIDModel, TimeStampedModel):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="translations")
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name="module_translations",
    )
    title = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["module", "language"], name="uniq_module_translation_lang"
            )
        ]
        ordering = ["language__code"]

    def __str__(self) -> str:
        return f"{self.title} [{self.language.code}]"


class Lesson(UUIDModel, TimeStampedModel):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    bunny_video_id = models.CharField(max_length=120, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self) -> str:
        return f"lesson {self.pk}"


class LessonTranslation(UUIDModel, TimeStampedModel):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="translations")
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name="lesson_translations",
    )
    title = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "language"], name="uniq_lesson_translation_lang"
            )
        ]
        ordering = ["language__code"]

    def __str__(self) -> str:
        return f"{self.title} [{self.language.code}]"


class AccessGrant(UUIDModel, TimeStampedModel):
    """Acceso de un usuario a un curso o receta (webhook Stripe o alta manual)."""

    class Source(models.TextChoices):
        MANUAL = "manual", "Manual"
        PURCHASE = "purchase", "Compra"

    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="access_grants")
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="access_grants",
        null=True,
        blank=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="access_grants",
        null=True,
        blank=True,
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    is_revoked = models.BooleanField(default=False)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.MANUAL)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(course__isnull=False, recipe__isnull=True)
                    | models.Q(course__isnull=True, recipe__isnull=False)
                ),
                name="access_grant_one_product",
            ),
            models.UniqueConstraint(
                fields=["user", "course"],
                condition=models.Q(course__isnull=False),
                name="uniq_access_grant_course",
            ),
            models.UniqueConstraint(
                fields=["user", "recipe"],
                condition=models.Q(recipe__isnull=False),
                name="uniq_access_grant_recipe",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        target = self.course_id or self.recipe_id
        return f"grant {self.user_id} → {target}"


class VideoAccessToken(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name="video_access_tokens",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="video_access_tokens",
        null=True,
        blank=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="video_access_tokens",
        null=True,
        blank=True,
    )
    bunny_video_id = models.CharField(max_length=120)
    token = models.CharField(max_length=64)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"video-token {self.pk}"
