from http import HTTPStatus

from fastapi.testclient import TestClient

from app.models import User
from app.schemas import Token
from app.security import create_access_token


def test_login(client: TestClient, user: User):
    response = client.post(
        "/auth/token",
        data={"username": user.email, "password": user.clean_password},
    )

    Token.model_validate(response.json())
    assert response.status_code == HTTPStatus.OK


def test_login_no_email(client: TestClient):
    response = client.delete(
        "/users/1",
        headers={
            "Authorization": f"Bearer {
                create_access_token({'no-email': 'test'})
            }"
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_login_email_not_found(client: TestClient):
    response = client.delete(
        "/users/1",
        headers={
            "Authorization": f"Bearer {
                create_access_token({'sub': 'test@test.com'})
            }"
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
