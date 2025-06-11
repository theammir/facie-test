from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlmodel import select

from app.dependencies.database import SessionDep
from app.dependencies.llm import LLMDep, LLMException
from app.exceptions import APIException, handled_error
from app.models.episode import (
    AltEpisodeRequest,
    AltEpisodeResponse,
    ErrorResponse,
    PodcastEpisode,
    PodcastEpisodeDB,
)

router = APIRouter()


@handled_error
class EpisodeExists(APIException):
    def __init__(self, title: str) -> None:
        self.title = title

    @property
    def status_code(self) -> int:
        return 409

    def into_json(self) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"message": f"Episode with title `{self.title}` already exists."},
        )


@handled_error
class EpisodeNotFound(APIException):
    def __init__(self, id: int) -> None:
        self.id = id

    @property
    def status_code(self) -> int:
        return 404

    def into_json(self) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "message": f"Episode with id {self.id} could not have been found."
            },
        )


@router.get("/episodes")
async def get_episodes(session: SessionDep) -> list[PodcastEpisodeDB]:
    """
    Get all existing podcast episodes.
    """
    return list(session.exec(select(PodcastEpisodeDB)).all())


@router.post(
    "/episodes",
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {
            "model": ErrorResponse,
            "description": "Episode with similar title already exists",
        },
    },
)
async def add_episode(episode: PodcastEpisode, session: SessionDep) -> PodcastEpisodeDB:
    """
    Add new podcast episode if doesn't already exist with similar name.
    """
    if session.exec(
        select(PodcastEpisodeDB).where(PodcastEpisodeDB.title == episode.title)
    ).first():
        raise EpisodeExists(episode.title)

    db_episode = PodcastEpisodeDB.model_validate(episode)
    session.add(db_episode)
    session.commit()
    session.refresh(db_episode)
    return db_episode


@router.post(
    "/episodes/{episode_id}/generate_alternative",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Episode with this ID couldn't have been found",
        },
        500: {"model": ErrorResponse, "description": "Couldn't get the LLM's response"},
    },
)
async def generate_alternative(
    episode_id: int, payload: AltEpisodeRequest, session: SessionDep, llm: LLMDep
) -> AltEpisodeResponse:
    """
    Generate alternative title or description of a podcast episode by ID.
    """
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
