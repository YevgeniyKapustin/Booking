from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.core.errors import (
    BusinessError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)


def create_json_error(status_code: int, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        BusinessError, lambda _request, exc: create_json_error(400, exc)
    )
    app.add_exception_handler(
        NotFoundError, lambda _request, exc: create_json_error(404, exc)
    )
    app.add_exception_handler(
        ForbiddenError, lambda _request, exc: create_json_error(403, exc)
    )
    app.add_exception_handler(
        UnauthorizedError, lambda _request, exc: create_json_error(401, exc)
    )
