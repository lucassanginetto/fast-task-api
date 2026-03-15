from http import HTTPStatus

from fastapi.testclient import TestClient

from app.models import User
from app.schemas import Token, UserOut
from app.security import create_access_token


def test_get_root(client: TestClient):
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == "Server is running"


def test_login(client: TestClient, user: User):
    response = client.post(
        "/token",
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


def test_get_users(client: TestClient):
    response = client.get("/users")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_get_users_with_users(client: TestClient, user: User):
    user_out = UserOut.model_validate(user).model_dump()
    assert client.get("/users/").json() == [user_out]


def test_get_user(client: TestClient, user: User):
    response = client.get("/users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "Test",
        "email": "test@test.com",
        "id": 1,
    }


def test_get_user_fail(client: TestClient):
    response = client.get("/users/1")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_post_user(client: TestClient):
    response = client.post(
        "/users",
        json={
            "username": "alice",
            "email": "alice@test.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "username": "alice",
        "email": "alice@test.com",
        "id": 1,
    }


def test_post_user_usename_integrity_error(client: TestClient, user: User):
    client.post(
        "/users",
        json={
            "username": "fausto",
            "email": "fausto@example.com",
            "password": "secret",
        },
    )

    response = client.post(
        "/users",
        json={
            "username": "fausto",
            "email": "bob@example.com",
            "password": "mynewpassword",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        "detail": "User with username fausto already exists"
    }


def test_post_user_email_integrity_error(client: TestClient, user: User):
    client.post(
        "/users",
        json={
            "username": "fausto",
            "email": "fausto@example.com",
            "password": "secret",
        },
    )

    response = client.post(
        "/users",
        json={
            "username": "bob",
            "email": "fausto@example.com",
            "password": "mynewpassword",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        "detail": "User with email fausto@example.com already exists"
    }


def test_put_user(client: TestClient, user: User, token: str):
    response = client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "bob",
            "email": "bob@test.com",
            "password": "newsecret",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "bob",
        "email": "bob@test.com",
        "id": 1,
    }


def test_put_user_username_integrity_error(
    client: TestClient, user: User, token: str
):
    client.post(
        "/users",
        json={
            "username": "fausto",
            "email": "fausto@example.com",
            "password": "secret",
        },
    )

    response = client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "fausto",
            "email": "bob@example.com",
            "password": "mynewpassword",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        "detail": "User with username fausto already exists"
    }


def test_put_user_email_integrity_error(
    client: TestClient, user: User, token: str
):
    client.post(
        "/users",
        json={
            "username": "fausto",
            "email": "fausto@example.com",
            "password": "secret",
        },
    )

    response = client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "bob",
            "email": "fausto@example.com",
            "password": "mynewpassword",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        "detail": "User with email fausto@example.com already exists"
    }


"""
def test_put_user_fail(client: TestClient):
    response = client.put(
        "/users/1",
        json={
            "username": "alice",
            "email": "alice@test.com",
            "password": "oldsecret",
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}
"""


def test_delete_user(client: TestClient, user: User, token: str):
    response = client.delete(
        f"/users/{user.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b""


"""
def test_delete_user_fail(client: TestClient):
    response = client.delete("/users/1")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}
"""
