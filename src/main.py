from fastapi import FastAPI, status

import exceptions
from episode import PodcastEpisode
from exceptions import init_handlers

app = FastAPI()
init_handlers(app)

episodes: list[PodcastEpisode] = []


@app.get("/episodes")
async def get_episodes() -> list[PodcastEpisode]:
    return episodes


@app.post("/episodes", status_code=status.HTTP_201_CREATED)
async def add_episode(episode: PodcastEpisode):
    if any(existing.title == episode.title for existing in episodes):
        raise exceptions.EpisodeExists(episode.title)
    episodes.append(episode)
