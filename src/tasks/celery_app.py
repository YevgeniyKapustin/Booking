from celery import Celery  # type: ignore[import-untyped]

from src.core.config import settings

celery_app = Celery(
    "booking",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    enable_utc=True,
    timezone="UTC",
)

celery_app.autodiscover_tasks(["src.tasks"])
