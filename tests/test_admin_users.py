import pytest


@pytest.mark.django_db
class TestAdminUsers:
    def test_list_users_requires_staff(self, api_client, registered_user):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {registered_user['access']}")
        response = api_client.get("/api/v1/admin/users/")
        assert response.status_code == 403

    def test_list_users_unauthenticated(self, api_client):
        response = api_client.get("/api/v1/admin/users/")
        assert response.status_code == 401

    def test_list_users(self, staff_client, registered_user):
        response = staff_client.get("/api/v1/admin/users/")
        assert response.status_code == 200
        body = response.json()
        assert body["count"] >= 1
        emails = [item["email"] for item in body["results"]]
        assert registered_user["email"] in emails

    def test_list_users_search(self, staff_client, registered_user):
        email = registered_user["email"]
        response = staff_client.get(f"/api/v1/admin/users/?search={email.split('@')[0]}")
        assert response.status_code == 200
        assert response.json()["count"] >= 1

    def test_user_detail(self, staff_client, registered_user):
        user_id = registered_user["id"]
        response = staff_client.get(f"/api/v1/admin/users/{user_id}/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == user_id
        assert data["email"] == registered_user["email"]
        assert data["purchases"] == []
        assert "email" in data["auth_providers"]
