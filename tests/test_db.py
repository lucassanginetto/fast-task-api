from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


def test_add_user(session: Session, mock_db_time):
    with mock_db_time(User) as time:
        session.add(
            User(
                username="alice",
                password="secret",
                email="alice@test.com",
            )
        )
        session.commit()

    added_user = session.scalar(select(User).where(User.username == "alice"))

    assert added_user is not None
    assert asdict(added_user) == {
        "id": 1,
        "username": "alice",
        "password": "secret",
        "email": "alice@test.com",
        "created_at": time,
        "updated_at": time,
    }
