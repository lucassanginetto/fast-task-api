from http import HTTPStatus

from fastapi.testclient import TestClient


def test_get_root(client: TestClient):
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == "Server is running"
