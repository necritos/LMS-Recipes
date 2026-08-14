from django.contrib import admin

from apps.content.models import (
    AccessGrant,
    Lesson,
    LessonTranslation,
    Module,
    ModuleTranslation,
    VideoAccessToken,
)


class ModuleTranslationInline(admin.TabularInline):
    model = ModuleTranslation
    extra = 1


class LessonTranslationInline(admin.TabularInline):
    model = LessonTranslation
    extra = 1


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "sort_order", "is_active")
    inlines = [ModuleTranslationInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "module", "sort_order", "is_active", "bunny_video_id")
    inlines = [LessonTranslationInline]


@admin.register(AccessGrant)
class AccessGrantAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "recipe", "expires_at", "is_revoked", "source")
    list_filter = ("source", "is_revoked")


@admin.register(VideoAccessToken)
class VideoAccessTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "bunny_video_id", "expires_at", "created_at")
    readonly_fields = ("token",)
