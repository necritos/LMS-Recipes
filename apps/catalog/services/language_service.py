from django.db import transaction

from apps.catalog.models import Language
from apps.common.exceptions import BusinessError


def _normalize_code(code: str) -> str:
    return code.strip().lower()


@transaction.atomic
def create_language(*, code: str, name: str, is_active: bool = True) -> Language:
    code = _normalize_code(code)
    if Language.objects.filter(code=code).exists():
        raise BusinessError(
            "LANGUAGE_ALREADY_EXISTS",
            "Ya existe un idioma con este código.",
            http_status=409,
        )
    return Language.objects.create(code=code, name=name.strip(), is_active=is_active)


@transaction.atomic
def update_language(*, language: Language, **fields) -> Language:
    if "code" in fields:
        code = _normalize_code(fields["code"])
        if Language.objects.exclude(pk=language.pk).filter(code=code).exists():
            raise BusinessError(
                "LANGUAGE_ALREADY_EXISTS",
                "Ya existe un idioma con este código.",
                http_status=409,
            )
        fields["code"] = code
    if "name" in fields:
        fields["name"] = fields["name"].strip()

    for key, value in fields.items():
        setattr(language, key, value)
    language.save()
    return language
