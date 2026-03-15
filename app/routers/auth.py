from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import session
from app.models import User
from app.schemas import Token
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

OAuth2FormDependency = Annotated[OAuth2PasswordRequestForm, Depends()]
SessionDependency = Annotated[Session, Depends(session)]


@router.post("/token")
def login_for_access_token(
    form_data: OAuth2FormDependency,
    session: SessionDependency,
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
