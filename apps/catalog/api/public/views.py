from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.catalog.api.public.serializers import (
    PublicCategorySerializer,
    PublicCourseDetailSerializer,
    PublicCourseListSerializer,
    PublicLanguageSerializer,
    PublicRecipeDetailSerializer,
    PublicRecipeListSerializer,
)
from apps.catalog.selectors import (
    categories_for_public,
    courses_for_public,
    get_active_language,
    get_published_course,
    get_published_recipe,
    list_active_languages,
    recipes_for_public,
    resolve_language_code,
)


class LanguageListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicLanguageSerializer
    pagination_class = None

    @extend_schema(tags=["Public"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return list_active_languages()


class CategoryListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicCategorySerializer
    pagination_class = None

    @extend_schema(
        tags=["Public"],
        parameters=[OpenApiParameter("lang", str, description="Código de idioma (default: es)")],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        lang = resolve_language_code(self.request.query_params.get("lang"))
        language = get_active_language(code=lang)
        return categories_for_public(language=language)


class CourseListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicCourseListSerializer

    @extend_schema(
        tags=["Public"],
        parameters=[
            OpenApiParameter("lang", str),
            OpenApiParameter("category", str, description="Slug de categoría"),
            OpenApiParameter("search", str),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        params = self.request.query_params
        language = get_active_language(code=resolve_language_code(params.get("lang")))
        return courses_for_public(
            language=language,
            category_slug=params.get("category") or None,
            search=params.get("search") or None,
        )


class CourseDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicCourseDetailSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    @extend_schema(
        tags=["Public"],
        parameters=[OpenApiParameter("lang", str)],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        language = get_active_language(
            code=resolve_language_code(self.request.query_params.get("lang"))
        )
        return get_published_course(slug=self.kwargs["slug"], language=language)


class RecipeListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicRecipeListSerializer

    @extend_schema(
        tags=["Public"],
        parameters=[
            OpenApiParameter("lang", str),
            OpenApiParameter("category", str),
            OpenApiParameter("search", str),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        params = self.request.query_params
        language = get_active_language(code=resolve_language_code(params.get("lang")))
        return recipes_for_public(
            language=language,
            category_slug=params.get("category") or None,
            search=params.get("search") or None,
        )


class RecipeDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicRecipeDetailSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    @extend_schema(
        tags=["Public"],
        parameters=[OpenApiParameter("lang", str)],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        language = get_active_language(
            code=resolve_language_code(self.request.query_params.get("lang"))
        )
        return get_published_recipe(slug=self.kwargs["slug"], language=language)
