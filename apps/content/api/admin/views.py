from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.catalog.api.admin.views import AdminResponseMixin
from apps.catalog.models import Course
from apps.common.exceptions import BusinessError
from apps.common.permissions import IsStaffUser
from apps.content.api.admin.serializers import AdminLessonSerializer, AdminModuleSerializer
from apps.content.models import Lesson, Module
from apps.content.selectors import admin_lessons_for_module, admin_modules_for_course
from apps.content.services.curriculum_service import (
    create_lesson,
    create_module,
    delete_lesson,
    delete_module,
    update_lesson,
    update_module,
)


def _course_from_slug(slug: str) -> Course:
    course = Course.objects.filter(slug=slug).first()
    if course is None:
        raise BusinessError("COURSE_NOT_FOUND", "Curso no encontrado.", http_status=404)
    return course


@extend_schema_view(
    list=extend_schema(tags=["Admin — Content"]),
    retrieve=extend_schema(tags=["Admin — Content"]),
    create=extend_schema(tags=["Admin — Content"]),
    update=extend_schema(tags=["Admin — Content"]),
    partial_update=extend_schema(tags=["Admin — Content"]),
    destroy=extend_schema(tags=["Admin — Content"]),
)
class AdminModuleViewSet(AdminResponseMixin, viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    serializer_class = AdminModuleSerializer
    pagination_class = None

    def get_queryset(self):
        course = _course_from_slug(self.kwargs["course_slug"])
        return admin_modules_for_course(course=course)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = _course_from_slug(self.kwargs["course_slug"])
        module = create_module(course=course, **serializer.validated_data)
        output = self.get_serializer(module)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        module = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        module = update_module(module=module, **serializer.validated_data)
        output = self.get_serializer(module)
        return Response(output.data)

    def perform_destroy(self, instance):
        delete_module(module=instance)


@extend_schema_view(
    list=extend_schema(tags=["Admin — Content"]),
    retrieve=extend_schema(tags=["Admin — Content"]),
    create=extend_schema(tags=["Admin — Content"]),
    update=extend_schema(tags=["Admin — Content"]),
    partial_update=extend_schema(tags=["Admin — Content"]),
    destroy=extend_schema(tags=["Admin — Content"]),
)
class AdminLessonViewSet(AdminResponseMixin, viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    serializer_class = AdminLessonSerializer
    pagination_class = None

    def get_queryset(self):
        module = Module.objects.filter(pk=self.kwargs["module_id"]).first()
        if module is None:
            raise BusinessError("MODULE_NOT_FOUND", "Módulo no encontrado.", http_status=404)
        return admin_lessons_for_module(module=module)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        module = Module.objects.filter(pk=self.kwargs["module_id"]).first()
        if module is None:
            raise BusinessError("MODULE_NOT_FOUND", "Módulo no encontrado.", http_status=404)
        lesson = create_lesson(module=module, **serializer.validated_data)
        output = self.get_serializer(lesson)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        lesson = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        lesson = update_lesson(lesson=lesson, **serializer.validated_data)
        output = self.get_serializer(lesson)
        return Response(output.data)

    def perform_destroy(self, instance):
        delete_lesson(lesson=instance)


@extend_schema_view(
    retrieve=extend_schema(tags=["Admin — Content"]),
    update=extend_schema(tags=["Admin — Content"]),
    partial_update=extend_schema(tags=["Admin — Content"]),
    destroy=extend_schema(tags=["Admin — Content"]),
)
class AdminModuleDetailViewSet(AdminResponseMixin, viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    serializer_class = AdminModuleSerializer
    queryset = Module.objects.prefetch_related("translations__language", "lessons__translations")
    http_method_names = ["get", "patch", "put", "delete", "head", "options"]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        module = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        module = update_module(module=module, **serializer.validated_data)
        output = self.get_serializer(module)
        return Response(output.data)

    def perform_destroy(self, instance):
        delete_module(module=instance)


@extend_schema_view(
    retrieve=extend_schema(tags=["Admin — Content"]),
    update=extend_schema(tags=["Admin — Content"]),
    partial_update=extend_schema(tags=["Admin — Content"]),
    destroy=extend_schema(tags=["Admin — Content"]),
)
class AdminLessonDetailViewSet(AdminResponseMixin, viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    serializer_class = AdminLessonSerializer
    queryset = Lesson.objects.prefetch_related("translations__language")
    http_method_names = ["get", "patch", "put", "delete", "head", "options"]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        lesson = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        lesson = update_lesson(lesson=lesson, **serializer.validated_data)
        output = self.get_serializer(lesson)
        return Response(output.data)

    def perform_destroy(self, instance):
        delete_lesson(lesson=instance)
