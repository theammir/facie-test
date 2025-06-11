<div align="center"><h1>Facie AI Test Task</h1></div>

## Stack 🚄

* #### [FastAPI](https://fastapi.tiangolo.com/) and [SQLModel](https://sqlmodel.tiangolo.com/) for type safety with Pydantic 
* #### [uv](https://docs.astral.sh/uv/) for project management
* #### Deployment with [Docker](https://www.docker.com/)

## Features 🌞

* #### Custom automatically handled exception interface
* #### Implementation-agnostic dependency injection
* #### Fully testable API (Manual and Github Actions)
* #### Type annotated codebase

## Potential features and nitpicks 🌙

* #### Make more things configurable for production use
* #### Some clever caching
* #### Rate-limiting of expensive operations (.../generate_alternative) 

## API Showcase 🖌️

* ##### GET /episodes
  Retrieves all existing episodes.
* ##### POST /episodes
  Sample request data:
  ```json
  {
    "title": "The Future of AI",
    "description": "We discuss upcoming trends in artificial intelligence.",
    "host": "Joe Rogan"
  }
  ```
  Sample response data:
  ```json
  {
    "title": "The Future of AI",
    "id": 1,
    "description": "We discuss upcoming trends in artificial intelligence.",
    "host": "Joe Rogan"
  }
  ```
* ##### POST /episodes/{episode_id}/generate_alternative
  Generates an alternative title/description for an existing podcast
  Sample request data:
  ```json
  {
    "target": "description",
    "prompt": "Rewrite for Gen Z user"
  }
  ```
  Sample response data (hardcoded token amount):
  ```json
  {
    "original_episode": {
      "host": "Joe Rogan",
      "id": 1,
      "title": "The Future of AI",
      "description": "We discuss upcoming trends in artificial intelligence."
    },
    "target": "description",
    "prompt": "Rewrite for Gen Z user",
    "generated_alternative": "🚀 AI Trends You NEED to Know in 2024! 🤖💥  \n\nFrom mind-blowing AI tools to wild future predictions—we’re breaking down the hottest tech you can’t ignore. Think ChatGPT on steroids, AI influencers"
  }
  ```

## Setup ⚙️

Rename `.env.example` to `.env` and set the following variables:
* `DB_URI` if the default is not sufficient.
* `DEEPSEEK_API_KEY` (generate one [here](https://platform.deepseek.com/api_keys)).

Run with Docker:
```bash
$ docker build --target release -t facie:latest . \
  && docker run --rm -p 8000:8000 facie:latest
```

Alternatively, use uv:
```bash
$ uv run fastapi run
```
It will automatically create a virtual environment.

If you prefer it completely bare-bones, consider:
```bash
$ python -m venv .venv
$ . .venv/bin/activate
(.venv) $ pip install .
(.venv) $ fastapi run
```

Test via `pytest`.

## Development thoughts 💡

There's usually a long rant here. I really like writing READMEs because they
make my work feel substantial at a glance.

First things that I addressed before actually implementing features are
exceptions and DI: I discovered that there's no automated handling of custom
exceptions in FastAPI, so I made an abstract interface for one to be able to
convert into `JSONResponse`, and made a simple decorator to generate a handler
for it.
```python
@handled_error
class EpisodeExists(APIException):
    def __init__(self, title: str) -> None:
        self.title = title

    @property
    def status_code(self) -> int:
        return 409  # This is where `TestClient` responses get their status code from

    def into_json(self) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"message": f"Episode with title `{self.title}` already exists."},
        )
```
Making these show up in Swagger docs still takes additional manual effort, though.

For dependency injection, I created a separate package, where each exports
dependencies and can optionally define `init_dependency`. All modules are
listed in the package `__init__.py`, and the app initializes them during
startup. This is not necessarily the best approach, as it's either documented
or nobody ever knows about it when writing new dependencies.

For an LLM prompter, that is also injected, I thought that it would be unwise
to inject a third-party directly, so I abstracted it as:
```python
class LLMPrompter(abc.ABC):
    @abc.abstractmethod
    def prompt(self, prompt_sys: str, prompt_user: str) -> str: ...

LLMDep = Annotated[LLMPrompter, Depends(get_prompter)]
```
That way, it's possible to define a concrete `DeepSeekPrompter` and create it
inside `get_prompter`, without ever changing the contract that API handlers
use.
