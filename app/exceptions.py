import abc
from collections.abc import Awaitable, Callable
from typing import Type, TypeVar

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class APIException(Exception, abc.ABC):
    @abc.abstractmethod
    def into_json(self) -> JSONResponse: ...


GenericException = TypeVar("GenericException", bound=APIException)
Handler = Callable[[Request, GenericException], Awaitable[JSONResponse]]

__exception_handlers: dict[Type[APIException], Handler] = {}


def init_handlers(app: FastAPI) -> None:
    for exception, handler in __exception_handlers.items():
        app.add_exception_handler(exception, handler)


def handled_error(class_: Type[GenericException]):
    async def inner_handler(request: Request, exc: GenericException) -> JSONResponse:
        return exc.into_json()

    __exception_handlers[class_] = inner_handler

    return class_


@handled_error
class EpisodeExists(APIException):
    def __init__(self, title: str) -> None:
        self.title = title

    def into_json(self) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"message": "Episode with this title already exists."},
        )
