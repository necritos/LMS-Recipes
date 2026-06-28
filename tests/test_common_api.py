from apps.common.exceptions import BusinessError


def test_business_error_attributes():
    error = BusinessError(
        "TEST_CODE",
        "Mensaje de prueba",
        http_status=400,
        details={"field": "value"},
    )
    assert error.code == "TEST_CODE"
    assert error.message == "Mensaje de prueba"
    assert error.http_status == 400
    assert error.details == {"field": "value"}


def test_public_ping_uses_envelope(api_client):
    response = api_client.get("/api/v1/public/ping/")
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "data": {"message": "pong", "service": "recetario-api"},
        "meta": {},
    }
