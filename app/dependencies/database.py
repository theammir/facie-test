import os
from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

__all__ = ("init_dependency", "SessionDep")


engine: Engine


def init_dependency() -> None:
    global engine
    uri = os.environ.get("DB_URI")
    if not uri:
        return

    engine = create_engine(uri, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
