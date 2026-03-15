from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import session
from app.models import User
from app.schemas import FilterPage, UserIn, UserOut
from app.security import current_user, hash_password

router = APIRouter(prefix="/users", tags=["users"])

SessionDependency = Annotated[Session, Depends(session)]
CurrentUserDependency = Annotated[User, Depends(current_user)]


@router.get("/")
def get_users(
    session: SessionDependency,
    filter_users: Annotated[FilterPage, Query()],
) -> list[UserOut]:
    return list(
        map(
            UserOut.model_validate,
            session.scalars(
                select(User)
                .offset(filter_users.offset)
                .limit(filter_users.limit)
            ).all(),
        )
    )


@router.get("/{id}")
def get_user(id: int, session: SessionDependency) -> UserOut:
    db_user = session.scalar(select(User).where(User.id == id))
    if db_user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserOut.model_validate(db_user)


@router.post("/", status_code=status.HTTP_201_CREATED)
def post_user(user_in: UserIn, session: SessionDependency) -> UserOut:
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


@router.put("/{id}")
def put_user(
    id: int,
    user_in: UserIn,
    session: SessionDependency,
    current_user: CurrentUserDependency,
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


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: int,
    session: SessionDependency,
    current_user: CurrentUserDependency,
) -> None:
    if current_user.id != id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    session.delete(current_user)
    session.commit()
