from http import HTTPStatus

from fastapi.testclient import TestClient


def test_get_root(client: TestClient):
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == "Server is running"


def test_post_user(client: TestClient):
    response = client.post(
        "/users/",
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


def test_get_users(client: TestClient):
    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            "username": "alice",
            "email": "alice@test.com",
            "id": 1,
        }
    ]


def test_get_user(client: TestClient):
    response = client.get("/users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "alice",
        "email": "alice@test.com",
        "id": 1,
    }


def test_get_user_fail(client: TestClient):
    response = client.get("/users/2")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_put_user(client: TestClient):
    response = client.put(
        "/users/1",
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


def test_delete_user(client: TestClient):
    response = client.delete("/users/1")

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b""


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


def test_delete_user_fail(client: TestClient):
    response = client.delete("/users/1")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}
