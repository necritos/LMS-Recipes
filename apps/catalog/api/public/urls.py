from django.urls import path

from apps.catalog.api.public.views import (
    CategoryListView,
    CourseDetailView,
    CourseListView,
    LanguageListView,
    RecipeDetailView,
    RecipeListView,
)

urlpatterns = [
    path("languages/", LanguageListView.as_view(), name="public-languages"),
    path("categories/", CategoryListView.as_view(), name="public-categories"),
    path("courses/", CourseListView.as_view(), name="public-courses"),
    path("courses/<slug:slug>/", CourseDetailView.as_view(), name="public-course-detail"),
    path("recipes/", RecipeListView.as_view(), name="public-recipes"),
    path("recipes/<slug:slug>/", RecipeDetailView.as_view(), name="public-recipe-detail"),
]
