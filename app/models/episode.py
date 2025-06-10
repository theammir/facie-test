from typing import Literal

from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Field, SQLModel

from app.exceptions import APIException, handled_error


class PodcastEpisode(SQLModel):
    title: str = Field(default=None, index=True)
    description: str = Field(default=None)
    host: str = Field(default=None)


class PodcastEpisodeDB(PodcastEpisode, table=True):
    id: int = Field(default=None, primary_key=True)


class AltEpisodeRequest(BaseModel):
    target: Literal["title", "description"]
    prompt: str


class AltEpisodeResponse(BaseModel):
    original_episode: PodcastEpisodeDB
    target: Literal["title", "description"]
    prompt: str
    generated_alternative: str


@handled_error
class EpisodeExists(APIException):
    def __init__(self, title: str) -> None:
        self.title = title

    def into_json(self) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"message": f"Episode with title `{self.title}` already exists."},
        )


@handled_error
class EpisodeNotFound(APIException):
    def __init__(self, id: int) -> None:
        self.id = id

    def into_json(self) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "message": f"Episode with id {self.id} could not have been found."
            },
        )
