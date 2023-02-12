from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

import exceptions

__all__ = ('include_exception_handlers',)


def on_already_in_exists_in_database_exception(
        request: Request,
        exc: exceptions.AlreadyExistsInDatabase,
) -> JSONResponse:
    return JSONResponse(
        content={'detail': str(exc)},
        status_code=status.HTTP_409_CONFLICT,
    )


def on_does_not_exist_in_database_exception(
        request: Request,
        exc: exceptions.DoesNotExistInDatabase,
) -> JSONResponse:
    return JSONResponse(
        content={'detail': str(exc)},
        status_code=status.HTTP_404_NOT_FOUND,
    )


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        exceptions.AlreadyExistsInDatabase,
        on_already_in_exists_in_database_exception
    )
    app.add_exception_handler(
        exceptions.DoesNotExistInDatabase,
        on_does_not_exist_in_database_exception,
    )
