from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.catalog.api.admin.views import (
    CategoryViewSet,
    CourseResourceDetailViewSet,
    CourseResourceViewSet,
    CourseViewSet,
    LanguageViewSet,
    RecipeViewSet,
)

router = DefaultRouter()
router.register("languages", LanguageViewSet, basename="admin-languages")
router.register("categories", CategoryViewSet, basename="admin-categories")
router.register("courses", CourseViewSet, basename="admin-courses")
router.register("recipes", RecipeViewSet, basename="admin-recipes")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "courses/<slug:course_slug>/resources/",
        CourseResourceViewSet.as_view({"get": "list", "post": "create"}),
        name="admin-course-resources",
    ),
    path(
        "resources/<uuid:pk>/",
        CourseResourceDetailViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="admin-resource-detail",
    ),
    path(
        "resources/<uuid:pk>/file/",
        CourseResourceDetailViewSet.as_view({"get": "download"}),
        name="admin-resource-file",
    ),
]
