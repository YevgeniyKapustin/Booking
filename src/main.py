from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.api import api_router
from src.core.config import settings
from src.core.exception_handlers import add_exception_handlers
from src.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    new_app = FastAPI(title=settings.app_name)
    add_exception_handlers(new_app)
    new_app.include_router(api_router)
    Instrumentator().instrument(new_app).expose(new_app, include_in_schema=False)
    return new_app


app = create_app()
