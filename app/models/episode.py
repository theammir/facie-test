from sqlmodel import Field, SQLModel


class PodcastEpisode(SQLModel):
    title: str = Field(default=None, index=True)
    description: str = Field(default=None)
    host: str = Field(default=None)


class PodcastEpisodeDB(PodcastEpisode, table=True):
    id: int = Field(default=None, primary_key=True)
