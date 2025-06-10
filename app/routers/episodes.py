from fastapi import APIRouter, status
from sqlmodel import select

from app import exceptions
from app.dependencies.database import SessionDep
from app.models.episode import PodcastEpisode, PodcastEpisodeDB

router = APIRouter()


@router.get("/episodes")
async def get_episodes(session: SessionDep) -> list[PodcastEpisodeDB]:
    return list(session.exec(select(PodcastEpisodeDB)).all())


@router.post(
    "/episodes",
    status_code=status.HTTP_201_CREATED,
)
async def add_episode(episode: PodcastEpisode, session: SessionDep) -> PodcastEpisodeDB:
    if session.exec(
        select(PodcastEpisodeDB).where(PodcastEpisodeDB.title == episode.title)
    ).first():
        raise exceptions.EpisodeExists(episode.title)

    db_episode = PodcastEpisodeDB.model_validate(episode)
    session.add(db_episode)
    session.commit()
    session.refresh(db_episode)
    return db_episode
