from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.catalog.api.admin.serializers import (
    AdminCategorySerializer,
    AdminCategoryWriteSerializer,
    AdminCourseSerializer,
    AdminCourseWriteSerializer,
    AdminLanguageSerializer,
    AdminRecipeSerializer,
    AdminRecipeWriteSerializer,
)
from apps.catalog.models import Category, Course, Language, Recipe
from apps.catalog.services.category_service import create_category, update_category
from apps.catalog.services.course_service import create_course, delete_course, update_course
from apps.catalog.services.language_service import create_language, update_language
from apps.catalog.services.recipe_service import create_recipe, delete_recipe, update_recipe
from apps.common.permissions import IsStaffUser


class AdminResponseMixin:
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if (
            response.status_code < 400
            and hasattr(response, "data")
            and isinstance(response.data, dict)
            and "data" not in response.data
            and "results" not in response.data
        ):
            response.data = {"data": response.data, "meta": {}}
        return response


@extend_schema_view(
    list=extend_schema(tags=["Admin — Catalog"]),
    retrieve=extend_schema(tags=["Admin — Catalog"]),
    create=extend_schema(tags=["Admin — Catalog"]),
    update=extend_schema(tags=["Admin — Catalog"]),
    partial_update=extend_schema(tags=["Admin — Catalog"]),
)
class LanguageViewSet(AdminResponseMixin, viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    queryset = Language.objects.all().order_by("code")
    serializer_class = AdminLanguageSerializer
    lookup_field = "code"
    lookup_value_regex = "[^/]+"

    def perform_create(self, serializer):
        self.instance = create_language(**serializer.validated_data)

    def perform_update(self, serializer):
        update_language(language=self.get_object(), **serializer.validated_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = self.get_serializer(self.instance)
        return Response(output.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(tags=["Admin — Catalog"]),
    retrieve=extend_schema(tags=["Admin — Catalog"]),
    create=extend_schema(tags=["Admin — Catalog"]),
    update=extend_schema(tags=["Admin — Catalog"]),
    partial_update=extend_schema(tags=["Admin — Catalog"]),
    destroy=extend_schema(tags=["Admin — Catalog"]),
)
class CategoryViewSet(AdminResponseMixin, viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    queryset = Category.objects.prefetch_related("translations__language").order_by(
        "sort_order", "slug"
    )
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return AdminCategoryWriteSerializer
        return AdminCategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = create_category(**serializer.validated_data)
        output = AdminCategorySerializer(category, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        category = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        category = update_category(category=category, **serializer.validated_data)
        output = AdminCategorySerializer(category, context={"request": request})
        return Response(output.data)


@extend_schema_view(
    list=extend_schema(tags=["Admin — Catalog"]),
    retrieve=extend_schema(tags=["Admin — Catalog"]),
    create=extend_schema(tags=["Admin — Catalog"]),
    update=extend_schema(tags=["Admin — Catalog"]),
    partial_update=extend_schema(tags=["Admin — Catalog"]),
    destroy=extend_schema(tags=["Admin — Catalog"]),
)
class CourseViewSet(AdminResponseMixin, viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = Course.objects.prefetch_related("translations__language", "category").order_by(
        "sort_order", "slug"
    )
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return AdminCourseWriteSerializer
        return AdminCourseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = create_course(**serializer.validated_data)
        output = AdminCourseSerializer(course, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        course = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        course = update_course(course=course, **serializer.validated_data)
        output = AdminCourseSerializer(course, context={"request": request})
        return Response(output.data)

    def perform_destroy(self, instance):
        delete_course(course=instance)


@extend_schema_view(
    list=extend_schema(tags=["Admin — Catalog"]),
    retrieve=extend_schema(tags=["Admin — Catalog"]),
    create=extend_schema(tags=["Admin — Catalog"]),
    update=extend_schema(tags=["Admin — Catalog"]),
    partial_update=extend_schema(tags=["Admin — Catalog"]),
    destroy=extend_schema(tags=["Admin — Catalog"]),
)
class RecipeViewSet(AdminResponseMixin, viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = Recipe.objects.prefetch_related("translations__language", "category").order_by(
        "sort_order", "slug"
    )
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return AdminRecipeWriteSerializer
        return AdminRecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = create_recipe(**serializer.validated_data)
        output = AdminRecipeSerializer(recipe, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        recipe = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        recipe = update_recipe(recipe=recipe, **serializer.validated_data)
        output = AdminRecipeSerializer(recipe, context={"request": request})
        return Response(output.data)

    def perform_destroy(self, instance):
        delete_recipe(recipe=instance)
