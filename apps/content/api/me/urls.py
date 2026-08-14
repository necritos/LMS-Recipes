from django.urls import path

from apps.content.api.me.views import (
    MeCourseLessonsView,
    MeCourseListView,
    MeCourseProgressView,
    MeLessonCompleteView,
    MeLessonViewView,
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
        "progress/<uuid:course_id>/",
        MeCourseProgressView.as_view(),
        name="me-course-progress",
    ),
    path("recipes/", MeRecipeListView.as_view(), name="me-recipes"),
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
