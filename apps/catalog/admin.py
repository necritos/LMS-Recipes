from django.contrib import admin

from apps.catalog.models import (
    Category,
    CategoryTranslation,
    Course,
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


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("slug", "price", "status", "access_days")
    list_filter = ("status",)
    inlines = [CourseTranslationInline]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("slug", "price", "status", "access_type", "access_days")
    list_filter = ("status", "access_type")
    inlines = [RecipeTranslationInline]
