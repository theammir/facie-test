import os
from typing import Generator

import dotenv
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from app.dependencies.database import get_session
from app.dependencies.llm import LLMPrompter, get_prompter
from app.main import app


class TestPrompter(LLMPrompter):
    def prompt(self, prompt_sys: str, prompt_user: str) -> str:
        return "TEST PROMPTER OUTPUT"


@pytest.fixture(scope="session", autouse=True)
def load_env() -> None:
    env_file = dotenv.find_dotenv(".env.test", raise_error_if_not_found=True)
    dotenv.load_dotenv(env_file, override=True)


@pytest.fixture
def session() -> Generator[Session]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(session: Session) -> Generator[TestClient]:
    def get_test_session():
        return session

    app.dependency_overrides[get_session] = get_test_session

    def get_test_prompter() -> LLMPrompter:
        return TestPrompter()

    app.dependency_overrides[get_prompter] = get_test_prompter

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_get_episodes(client: TestClient):
    response = client.get("/episodes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


def test_add_episode(client: TestClient):
    sample_json = {
        "title": "The Future of AI",
        "description": "We discuss upcoming trends in artificial intelligence.",
        "host": "Joe Rogan",
    }

    response = client.post("/episodes", json=sample_json)
    assert response.status_code == 201
    assert len(response.json()) == 4  # Original keys + "id"
    assert response.json().get("id") is not None

    duplicate = client.post("/episodes", json=sample_json)
    assert duplicate.status_code == 409


def test_alternative(client: TestClient):
    sample_episode_json = {
        "title": "The Future of AI",
        "description": "We discuss upcoming trends in artificial intelligence.",
        "host": "Joe Rogan",
    }
    sample_alt_json = {"target": "description", "prompt": "Rewrite for Gen Z user"}

    assert len(client.get("/episodes").json()) == 0

    client.post("/episodes", json=sample_episode_json)
    response = client.post("/episodes/1/generate_alternative", json=sample_alt_json)
    assert response.status_code == 200

    original_db_episode = response.json()["original_episode"]
    del original_db_episode["id"]
    assert original_db_episode == sample_episode_json
