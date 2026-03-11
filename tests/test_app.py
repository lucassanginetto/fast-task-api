from http import HTTPStatus

from fastapi.testclient import TestClient

from app.main import app


def test_root_should_return_ok_and_server_running():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Server is running"}
