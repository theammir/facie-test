import abc
from typing import Type

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.types import HTTPExceptionHandler


class APIException(HTTPException, abc.ABC):
    @property
    @abc.abstractmethod
    def status_code(self) -> int: ...

    @abc.abstractmethod
    def into_json(self) -> JSONResponse: ...


__exception_handlers: dict[Type[APIException], HTTPExceptionHandler] = {}


def handled_error[E: APIException](class_: Type[E]) -> Type[E]:
    async def inner_handler(_: Request, exc: Exception) -> JSONResponse:
        # HTTPExceptionHandler requires a base `Exception` in its signature.
        # We know this handler is only used for `E`.
        if not isinstance(exc, class_):
            raise exc
        return exc.into_json()

    __exception_handlers[class_] = inner_handler

    return class_


def init_handlers(app: FastAPI) -> None:
    for exception, handler in __exception_handlers.items():
        app.add_exception_handler(exception, handler)
