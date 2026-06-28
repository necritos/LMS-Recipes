from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

from apps.common.exceptions import BusinessError


def recetario_exception_handler(exc, context):
    if isinstance(exc, BusinessError):
        exc = _business_to_api(exc)
    response = exception_handler(exc, context)
    if response is None:
        return None
    response.data = _normalize_error_payload(response.data, exc)
    return response


def _business_to_api(error: BusinessError) -> APIException:
    api_exc = APIException(
        detail={
            "code": error.code,
            "message": error.message,
            "details": error.details,
        }
    )
    api_exc.status_code = error.http_status
    return api_exc


def _normalize_error_payload(data, exc) -> dict:
    if isinstance(data, dict) and "error" in data:
        return data
    if isinstance(data, dict) and "code" in data and "message" in data:
        return {"error": data}
    if isinstance(data, list):
        return {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Los datos enviados no son válidos.",
                "details": {"fields": data},
            }
        }
    if isinstance(data, dict):
        code = getattr(exc, "default_code", "ERROR").upper().replace(" ", "_")
        if "detail" in data and len(data) == 1:
            detail = data["detail"]
            if isinstance(detail, dict) and "code" in detail:
                return {"error": detail}
            return {
                "error": {
                    "code": code,
                    "message": str(detail),
                    "details": None,
                }
            }
        return {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Los datos enviados no son válidos.",
                "details": data,
            }
        }
    return {
        "error": {
            "code": "ERROR",
            "message": str(data),
            "details": None,
        }
    }
