import abc
import os
from typing import Annotated

from deepseek import DeepSeekAPI
from fastapi import Depends
from fastapi.responses import JSONResponse

from app.exceptions import APIException, handled_error

__all__ = ("init_dependency", "LLMDep")

SYSTEM_PROMPT_PREFIX = "You work with podcast episodes' titles and descriptions. "
PROMPT_MAX_TOKENS = 50


def init_dependency() -> None:
    pass


class LLMPrompter(abc.ABC):
    @abc.abstractmethod
    def prompt(self, prompt_sys: str, prompt_user: str) -> str: ...


def get_prompter() -> LLMPrompter:
    # interchangeable logic
    deepseek = DeepSeekAPI(os.environ.get("DEEPSEEK_API_KEY"))
    return DeepSeekPrompter(deepseek)


LLMDep = Annotated[LLMPrompter, Depends(get_prompter)]


@handled_error
class LLMException(APIException):
    def __init__(self, message: str) -> None:
        self.message = message

    @property
    def status_code(self) -> int:
        return 500

    def into_json(self) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"message": f"Unexpected server error: {self.message}"},
        )


class DeepSeekPrompter(LLMPrompter):
    def __init__(self, client: DeepSeekAPI):
        self.__client = client

    def prompt(self, prompt_sys: str, prompt_user: str) -> str:
        completion = self.__client.chat_completion(
            prompt=prompt_user,
            prompt_sys=SYSTEM_PROMPT_PREFIX + prompt_sys,
            max_tokens=PROMPT_MAX_TOKENS,
        )
        return str(completion)
