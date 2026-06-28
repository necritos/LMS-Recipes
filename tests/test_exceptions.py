from apps.common.api.exceptions import recetario_exception_handler
from apps.common.exceptions import BusinessError


def test_business_error_handler_returns_normalized_payload():
    error = BusinessError("ACCESS_DENIED", "Acceso denegado.", http_status=403)
    response = recetario_exception_handler(error, {})
    assert response.status_code == 403
    assert response.data["error"]["code"] == "ACCESS_DENIED"
    assert response.data["error"]["message"] == "Acceso denegado."
    assert response.data["error"]["details"] in (None, "None")
