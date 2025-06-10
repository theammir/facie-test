from fastapi import APIRouter, status

from .. import exceptions
from ..models import PodcastEpisode

router = APIRouter()

episodes: list[PodcastEpisode] = []


@router.get("/episodes")
async def get_episodes() -> list[PodcastEpisode]:
    return episodes


@router.post("/episodes", status_code=status.HTTP_201_CREATED)
async def add_episode(episode: PodcastEpisode):
    if any(existing.title == episode.title for existing in episodes):
        raise exceptions.EpisodeExists(episode.title)
    episodes.append(episode)
    return episode
