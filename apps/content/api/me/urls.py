from django.urls import path

from apps.content.api.me.views import MeCourseLessonsView, MeRecipeVideoView

urlpatterns = [
    path(
        "courses/<uuid:course_id>/lessons/",
        MeCourseLessonsView.as_view(),
        name="me-course-lessons",
    ),
    path(
        "recipes/<uuid:recipe_id>/video/",
        MeRecipeVideoView.as_view(),
        name="me-recipe-video",
    ),
]
