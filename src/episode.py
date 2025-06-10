from pydantic import BaseModel


class PodcastEpisode(BaseModel):
    title: str
    description: str
    host: str
