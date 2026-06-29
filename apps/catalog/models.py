from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.catalog.constants import PublishStatus, RecipeAccessType
from apps.common.models import TimeStampedModel, UUIDModel


def cover_upload_path(instance, filename: str) -> str:
    folder = instance.__class__.__name__.lower()
    return f"{folder}s/covers/{instance.pk or 'new'}/{filename}"


class Language(UUIDModel, TimeStampedModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class Category(UUIDModel, TimeStampedModel):
    slug = models.SlugField(max_length=120, unique=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "slug"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.slug


class CategoryTranslation(UUIDModel, TimeStampedModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="translations",
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name="category_translations",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["category", "language"],
                name="uniq_category_translation_lang",
            ),
        ]
        ordering = ["language__code"]

    def __str__(self) -> str:
        return f"{self.category.slug} [{self.language.code}]"


class Course(UUIDModel, TimeStampedModel):
    slug = models.SlugField(max_length=160, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    access_days = models.PositiveIntegerField(default=365)
    cover_image = models.ImageField(upload_to=cover_upload_path, blank=True)
    status = models.CharField(
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "slug"]

    def __str__(self) -> str:
        return self.slug


class CourseTranslation(UUIDModel, TimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="translations",
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name="course_translations",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "language"],
                name="uniq_course_translation_lang",
            ),
        ]
        ordering = ["language__code"]

    def __str__(self) -> str:
        return f"{self.course.slug} [{self.language.code}]"


class Recipe(UUIDModel, TimeStampedModel):
    slug = models.SlugField(max_length=160, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recipes",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    access_type = models.CharField(
        max_length=20,
        choices=RecipeAccessType.choices,
        default=RecipeAccessType.LIFETIME,
    )
    access_days = models.PositiveIntegerField(null=True, blank=True)
    cover_image = models.ImageField(upload_to=cover_upload_path, blank=True)
    status = models.CharField(
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "slug"]

    def __str__(self) -> str:
        return self.slug


class RecipeTranslation(UUIDModel, TimeStampedModel):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="translations",
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name="recipe_translations",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "language"],
                name="uniq_recipe_translation_lang",
            ),
        ]
        ordering = ["language__code"]

    def __str__(self) -> str:
        return f"{self.recipe.slug} [{self.language.code}]"
