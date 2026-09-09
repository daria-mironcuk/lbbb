from fastapi.testclient import TestClient


def test_users_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/users")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)