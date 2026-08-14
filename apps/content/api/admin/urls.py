from django.urls import path

from apps.content.api.admin.views import (
    AdminLessonDetailViewSet,
    AdminLessonViewSet,
    AdminModuleDetailViewSet,
    AdminModuleViewSet,
)

urlpatterns = [
    path(
        "courses/<slug:course_slug>/modules/",
        AdminModuleViewSet.as_view({"get": "list", "post": "create"}),
        name="admin-course-modules",
    ),
    path(
        "modules/<uuid:pk>/",
        AdminModuleDetailViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="admin-module-detail",
    ),
    path(
        "modules/<uuid:module_id>/lessons/",
        AdminLessonViewSet.as_view({"get": "list", "post": "create"}),
        name="admin-module-lessons",
    ),
    path(
        "lessons/<uuid:pk>/",
        AdminLessonDetailViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="admin-lesson-detail",
    ),
]
