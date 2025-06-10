from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.dependencies.database import SessionDep
from app.dependencies.llm import LLMDep, LLMException
from app.models.episode import (
    AltEpisodeRequest,
    AltEpisodeResponse,
    EpisodeExists,
    EpisodeNotFound,
    PodcastEpisode,
    PodcastEpisodeDB,
)

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
        raise EpisodeExists(episode.title)

    db_episode = PodcastEpisodeDB.model_validate(episode)
    session.add(db_episode)
    session.commit()
    session.refresh(db_episode)
    return db_episode


@router.post("/episodes/{episode_id}/generate_alternative")
async def generate_alternative_desc(
    episode_id: int, payload: AltEpisodeRequest, session: SessionDep, llm: LLMDep
) -> AltEpisodeResponse:
    db_episode = session.exec(
        select(PodcastEpisodeDB).where(PodcastEpisodeDB.id == episode_id)
    ).first()

    if not db_episode:
        raise EpisodeNotFound(episode_id)

    original = db_episode.title if payload.target == "title" else db_episode.description
    try:
        alternative = llm.prompt(payload.prompt, original)
    except Exception as e:
        raise LLMException(str(e))

    return AltEpisodeResponse(
        original_episode=db_episode,
        target=payload.target,
        prompt=payload.prompt,
        generated_alternative=alternative,
    )
