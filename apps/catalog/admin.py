from django.contrib import admin

from apps.catalog.models import (
    Category,
    CategoryTranslation,
    Course,
    CourseResource,
    CourseResourceTranslation,
    CourseTranslation,
    Language,
    Recipe,
    RecipeTranslation,
)


class CategoryTranslationInline(admin.TabularInline):
    model = CategoryTranslation
    extra = 1


class CourseTranslationInline(admin.TabularInline):
    model = CourseTranslation
    extra = 1


class RecipeTranslationInline(admin.TabularInline):
    model = RecipeTranslation
    extra = 1


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    list_filter = ("is_active",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "sort_order", "is_active")
    inlines = [CategoryTranslationInline]


class CourseResourceTranslationInline(admin.TabularInline):
    model = CourseResourceTranslation
    extra = 1


class CourseResourceInline(admin.TabularInline):
    model = CourseResource
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("slug", "format", "price", "status", "access_days", "event_starts_at")
    list_filter = ("status", "format")
    inlines = [CourseTranslationInline, CourseResourceInline]


@admin.register(CourseResource)
class CourseResourceAdmin(admin.ModelAdmin):
    list_display = ("original_name", "course", "kind", "sort_order", "is_active")
    list_filter = ("kind", "is_active")
    inlines = [CourseResourceTranslationInline]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("slug", "price", "status", "access_type", "access_days", "bunny_video_id")
    list_filter = ("status", "access_type")
    inlines = [RecipeTranslationInline]
