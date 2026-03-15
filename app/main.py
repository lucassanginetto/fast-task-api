from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import session
from app.models import User
from app.schemas import Token, UserIn, UserOut
from app.security import (
    create_access_token,
    current_user,
    hash_password,
    verify_password,
)

app = FastAPI()


@app.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(session)],
) -> Token:
    user = session.scalar(select(User).where(User.email == form_data.username))
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )

    access_token = create_access_token({"sub": user.email})

    return Token(access_token=access_token, token_type="bearer")


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

    hashed_password = hash_password(user_in.password)

    db_user = User(
        username=user_in.username,
        password=hashed_password,
        email=user_in.email,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return UserOut.model_validate(db_user)


@app.put("/users/{id}")
def put_user(
    id: int,
    user_in: UserIn,
    session: Annotated[Session, Depends(session)],
    current_user: Annotated[User, Depends(current_user)],
) -> UserOut:
    if current_user.id != id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        current_user.username = user_in.username
        current_user.password = hash_password(user_in.password)
        current_user.email = user_in.email
        session.commit()
        session.refresh(current_user)

        return UserOut.model_validate(current_user)

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
    id: int,
    session: Annotated[Session, Depends(session)],
    current_user: Annotated[User, Depends(current_user)],
) -> None:
    if current_user.id != id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    session.delete(current_user)
    session.commit()


@app.get("/")
def get_root() -> str:
    return "Server is running"
