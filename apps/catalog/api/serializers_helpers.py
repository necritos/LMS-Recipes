import json

from rest_framework import serializers


class TranslationInputSerializer(serializers.Serializer):
    language_code = serializers.CharField(max_length=10)
    name = serializers.CharField(max_length=200, required=False)
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    meta_title = serializers.CharField(required=False, allow_blank=True, default="")
    meta_description = serializers.CharField(required=False, allow_blank=True, default="")


class JSONTranslationsMixin:
    """Mixin con validación de traducciones. Declara `translations` en cada Serializer."""

    def validate_translations(self, value):
        if not value:
            raise serializers.ValidationError("Debes incluir al menos una traducción.")
        return value

    def to_internal_value(self, data):
        mutable = data.copy() if hasattr(data, "copy") else dict(data)
        raw = mutable.get("translations")
        if isinstance(raw, str):
            try:
                mutable["translations"] = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError(
                    {"translations": "JSON inválido en traducciones."}
                ) from exc
        return super().to_internal_value(mutable)


def get_active_translation(obj, attr: str, default=""):
    translations = getattr(obj, "active_translations", None)
    if translations:
        return getattr(translations[0], attr, default)
    if hasattr(obj, "translations"):
        first = obj.translations.first()
        if first:
            return getattr(first, attr, default)
    return default
