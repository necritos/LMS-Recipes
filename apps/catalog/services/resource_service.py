from django.db import transaction
from django.http import FileResponse

from apps.catalog.constants import CourseFormat, CourseResourceKind
from apps.catalog.models import Course, CourseResource, CourseResourceTranslation
from apps.catalog.services.category_service import _get_language_map
from apps.common.exceptions import BusinessError


def resource_file_response(*, resource: CourseResource) -> FileResponse:
    if not resource.file:
        raise BusinessError(
            "RESOURCE_FILE_MISSING",
            "El recurso no tiene archivo.",
            http_status=404,
        )
    handle = resource.file.open("rb")
    filename = resource.original_name or resource.file.name.rsplit("/", 1)[-1]
    response = FileResponse(handle, as_attachment=True, filename=filename)
    if resource.content_type:
        response["Content-Type"] = resource.content_type
    return response


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".heic", ".bmp"}


def assert_course_allows_resources(*, course: Course) -> None:
    if course.format == CourseFormat.IN_PERSON:
        raise BusinessError(
            "IN_PERSON_NO_RESOURCES",
            "Los cursos presenciales no tienen recursos descargables.",
            http_status=422,
        )


def infer_resource_kind(*, filename: str = "", content_type: str = "") -> str:
    name = (filename or "").lower()
    ctype = (content_type or "").lower()
    if ctype == "application/pdf" or name.endswith(".pdf"):
        return CourseResourceKind.PDF
    if ctype.startswith("image/") or any(name.endswith(ext) for ext in IMAGE_EXTENSIONS):
        return CourseResourceKind.IMAGE
    return CourseResourceKind.FILE


def _upsert_resource_translations(*, resource: CourseResource, translations: list[dict]) -> None:
    if not translations:
        raise BusinessError(
            "TRANSLATIONS_REQUIRED",
            "Debes incluir al menos una traducción.",
            http_status=422,
        )
    resource.translations.all().delete()
    lang_map = _get_language_map([item["language_code"] for item in translations])
    for item in translations:
        language = lang_map[item["language_code"].strip().lower()]
        title = (item.get("title") or "").strip()
        if not title:
            raise BusinessError(
                "TRANSLATION_TITLE_REQUIRED",
                "Cada traducción del recurso necesita title.",
                http_status=422,
            )
        CourseResourceTranslation.objects.create(
            resource=resource,
            language=language,
            title=title,
            description=item.get("description", "") or "",
        )


def _file_meta(upload) -> tuple[str, str]:
    original_name = getattr(upload, "name", "") or ""
    content_type = getattr(upload, "content_type", "") or ""
    return original_name[:255], content_type[:120]


@transaction.atomic
def create_course_resource(
    *,
    course: Course,
    file,
    translations: list[dict],
    kind: str | None = None,
    sort_order: int = 0,
    is_active: bool = True,
) -> CourseResource:
    assert_course_allows_resources(course=course)
    original_name, content_type = _file_meta(file)
    resource = CourseResource(
        course=course,
        kind=kind or infer_resource_kind(filename=original_name, content_type=content_type),
        original_name=original_name,
        content_type=content_type,
        sort_order=sort_order,
        is_active=is_active,
    )
    resource.file = file
    resource.save()
    _upsert_resource_translations(resource=resource, translations=translations)
    return resource


@transaction.atomic
def update_course_resource(*, resource: CourseResource, **fields) -> CourseResource:
    assert_course_allows_resources(course=resource.course)
    translations = fields.pop("translations", None)
    upload = fields.pop("file", None)

    if upload is not None:
        original_name, content_type = _file_meta(upload)
        resource.file = upload
        resource.original_name = original_name
        resource.content_type = content_type
        if "kind" not in fields:
            resource.kind = infer_resource_kind(filename=original_name, content_type=content_type)

    for key, value in fields.items():
        setattr(resource, key, value)
    resource.save()

    if translations is not None:
        _upsert_resource_translations(resource=resource, translations=translations)
    return resource


@transaction.atomic
def delete_course_resource(*, resource: CourseResource) -> None:
    resource.delete()
