from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import session
from app.models import User
from app.schemas import UserIn, UserOut

app = FastAPI()


@app.get("/users/")
def get_users(
    session: Annotated[Session, Depends(session)],
    skip: int = 0,
    limit: int = 100,
) -> list[UserOut]:
    return list(
        map(
            UserOut.model_validate,
            session.scalars(select(User).offset(skip).limit(limit)).all(),
        )
    )


@app.get("/users/{id}")
def get_user(
    id: int, session: Annotated[Session, Depends(session)]
) -> UserOut:
    db_user = session.scalar(select(User).where(User.id == id))
    if db_user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserOut.model_validate(db_user)


@app.post("/users/", status_code=status.HTTP_201_CREATED)
def post_user(
    user_in: UserIn, session: Annotated[Session, Depends(session)]
) -> UserOut:
    db_user = session.scalar(
        select(User).where(
            (User.username == user_in.username) | (User.email == user_in.email)
        )
    )
    if db_user is not None:
        if db_user.username == user_in.username:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=f"User with username {user_in.username} already exists",
            )
        else:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=f"User with email {user_in.email} already exists",
            )

    db_user = User(
        username=user_in.username,
        password=user_in.password,
        email=user_in.email,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return UserOut.model_validate(db_user)


@app.put("/users/{id}")
def put_user(
    id: int, user_in: UserIn, session: Annotated[Session, Depends(session)]
) -> UserOut:
    db_user = session.scalar(select(User).where(User.id == id))
    if db_user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        db_user.username = user_in.username
        db_user.password = user_in.password
        db_user.email = user_in.email
        session.commit()
        session.refresh(db_user)

        return UserOut.model_validate(db_user)

    except IntegrityError as e:
        e_orig_str = str(e.orig)
        if "users.username" in e_orig_str:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=f"User with username {user_in.username} already exists",
            )
        elif "users.email" in e_orig_str:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=f"User with email {user_in.email} already exists",
            )
        else:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@app.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: int, session: Annotated[Session, Depends(session)]
) -> None:
    db_user = session.scalar(select(User).where(User.id == id))
    if db_user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    session.delete(db_user)
    session.commit()


@app.get("/")
def get_root() -> str:
    return "Server is running"
