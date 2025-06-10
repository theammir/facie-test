from typing import Literal

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


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
