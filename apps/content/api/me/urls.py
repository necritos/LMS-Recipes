from django.urls import path

from apps.content.api.me.views import (
    MeCourseLessonsView,
    MeCourseListView,
    MeCourseProgressView,
    MeCourseResourceFileView,
    MeCourseResourcesView,
    MeLessonCompleteView,
    MeLessonViewView,
    MeRecipeDetailView,
    MeRecipeListView,
    MeRecipeVideoView,
)

urlpatterns = [
    path("courses/", MeCourseListView.as_view(), name="me-courses"),
    path(
        "courses/<uuid:course_id>/lessons/",
        MeCourseLessonsView.as_view(),
        name="me-course-lessons",
    ),
    path(
        "courses/<uuid:course_id>/resources/",
        MeCourseResourcesView.as_view(),
        name="me-course-resources",
    ),
    path(
        "courses/<uuid:course_id>/resources/<uuid:resource_id>/file/",
        MeCourseResourceFileView.as_view(),
        name="me-course-resource-file",
    ),
    path(
        "progress/<uuid:course_id>/",
        MeCourseProgressView.as_view(),
        name="me-course-progress",
    ),
    path("recipes/", MeRecipeListView.as_view(), name="me-recipes"),
    path(
        "recipes/<uuid:recipe_id>/",
        MeRecipeDetailView.as_view(),
        name="me-recipe-detail",
    ),
    path(
        "recipes/<uuid:recipe_id>/video/",
        MeRecipeVideoView.as_view(),
        name="me-recipe-video",
    ),
    path(
        "lessons/<uuid:lesson_id>/complete/",
        MeLessonCompleteView.as_view(),
        name="me-lesson-complete",
    ),
    path(
        "lessons/<uuid:lesson_id>/view/",
        MeLessonViewView.as_view(),
        name="me-lesson-view",
    ),
]
