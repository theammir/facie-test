from typing import Annotated, Generator

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

__all__ = ("init_dependency", "SessionDep")

SQLITE_FILENAME = "db.sqlite"

engine = create_engine(
    f"sqlite:///{SQLITE_FILENAME}", connect_args={"check_same_thread": False}
)


def init_dependency() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
