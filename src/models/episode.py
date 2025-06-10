from sqlmodel import Field, SQLModel


class PodcastEpisode(SQLModel, table=True):
    title: str = Field(default=None, primary_key=True)
    description: str = Field(default=None)
    host: str = Field(default=None)
