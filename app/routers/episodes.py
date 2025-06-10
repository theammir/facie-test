from fastapi import APIRouter, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import select

from .. import exceptions
from ..dependencies.database import SessionDep
from ..models import PodcastEpisode

router = APIRouter()


@router.get("/episodes")
async def get_episodes(session: SessionDep) -> list[PodcastEpisode]:
    return list(session.exec(select(PodcastEpisode)).all())


@router.post("/episodes", status_code=status.HTTP_201_CREATED)
async def add_episode(episode: PodcastEpisode, session: SessionDep) -> PodcastEpisode:
    episode_exists = True
    try:
        session.get_one(PodcastEpisode, episode.title)
    except NoResultFound:
        episode_exists = False

    if episode_exists:
        raise exceptions.EpisodeExists(episode.title)

    session.add(episode)
    session.commit()
    session.refresh(episode)
    return episode
