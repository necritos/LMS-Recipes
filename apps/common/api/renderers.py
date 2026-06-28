from rest_framework.renderers import JSONRenderer


def _is_paginated_response(data) -> bool:
    return isinstance(data, dict) and "results" in data and "count" in data


class EnvelopeJSONRenderer(JSONRenderer):
    """Envuelve respuestas exitosas en { data, meta } salvo paginación DRF."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        if response is not None and response.status_code >= 400:
            return super().render(data, accepted_media_type, renderer_context)
        if _is_paginated_response(data):
            return super().render(data, accepted_media_type, renderer_context)
        if isinstance(data, dict) and "data" in data and "meta" in data:
            return super().render(data, accepted_media_type, renderer_context)
        if data is None:
            envelope = {"data": None, "meta": {}}
        elif isinstance(data, list):
            envelope = {"data": data, "meta": {}}
        else:
            envelope = {"data": data, "meta": {}}
        return super().render(envelope, accepted_media_type, renderer_context)
