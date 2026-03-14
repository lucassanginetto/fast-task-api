from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


def session():
    with Session(engine) as session:
        yield session
