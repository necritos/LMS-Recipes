from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.catalog.api.admin.views import (
    CategoryViewSet,
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
]
